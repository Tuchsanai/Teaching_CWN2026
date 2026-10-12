// rea-tools.mjs — ตัวช่วยเล็ก ๆ สำหรับต่อ Evidence ของ REA (ไม่มี dependency, Node ≥ 22)
// Evidence ของ REA ใหญ่ (หลายสิบ MB) → อย่าเปิดอ่านเอง ให้ใช้คำสั่งด้านล่างสรุป
//
//   node rea-tools.mjs view        <app-evidence.json> <out-view.json>            ทำ input ให้ `rea inspect-analysis-view` (summary)
//   node rea-tools.mjs endpoints   <app-evidence.json>                            endpoint ที่ REA กู้ได้ + ไฟล์ route ใน inventory
//   node rea-tools.mjs trace-input <app-evidence.json> <seed> <dir> <out.json>    ทำ input ให้ `rea trace-application-feature` (seed แบบ string)
//   node rea-tools.mjs trace-sum   <trace-out.json>                               สรุปผล trace (node ที่เจอ)
//   node rea-tools.mjs cmp-input   <left.json> <right.json> <out.json>            ทำ input ให้ `rea compare-application-versions`
//   node rea-tools.mjs cmp-sum     <compare-out.json>                             สรุปผลเทียบเวอร์ชัน (เฉพาะที่ changed)
//   node rea-tools.mjs har-records <file.har>                                     พิมพ์ --record ของ request /api/* (ไว้ต่อท้าย inspect-web-network-capture)
//   node rea-tools.mjs har-api     <inspect-web-network-capture-out.json>         ตาราง API inventory จากผล HAR ของ REA
import { readFileSync, writeFileSync } from "node:fs";

const [cmd, ...a] = process.argv.slice(2);
const load = (p) => JSON.parse(readFileSync(p, "utf8"));
const save = (p, o) => writeFileSync(p, JSON.stringify(o));
const label = (n) => {
  const p = n?.observations?.[0]?.properties ?? {};
  return `${n?.kind}:${p.path ?? ""}${p.module_key ? "#" + p.module_key : ""}${p.value ? " " + p.value : ""}`;
};

switch (cmd) {
  case "view":
    save(a[1], { source: { kind: "inline", evidence: load(a[0]) }, view: { kind: "summary" } });
    break;

  case "endpoints": {
    const g = load(a[0]).normalized_result.graph;
    console.log("## endpoint ที่ REA กู้ได้ (จากโค้ดฝั่งเบราว์เซอร์)");
    for (const n of g.nodes.filter((x) => x.kind === "endpoint"))
      for (const o of n.observations) console.log(`- ${o.properties.value}  (${o.properties.mechanism} @ ${o.evidence.location.value?.source ?? "?"})`);
    const routes = new Set();
    for (const n of g.nodes) for (const m of JSON.stringify(n).match(/app\/api\/[A-Za-z0-9\/\[\]\.-]*?\/route/g) ?? []) routes.add("/" + m.replace(/^app\//, "").replace(/\/route$/, ""));
    console.log(`\n## route ฝั่งเซิร์ฟเวอร์ที่เห็นจากชื่อไฟล์ chunks/app/api/**/route-*.js (${routes.size})`);
    console.log([...routes].sort().map((r) => "- " + r).join("\n"));
    const unk = g.nodes.filter((x) => x.kind === "unknown").map((x) => x.observations[0].properties.path);
    console.log(`\n## ไฟล์ที่ REA วิเคราะห์ไม่ครบ (unknown ${unk.length})\n` + unk.map((u) => "- " + u).join("\n"));
    break;
  }

  case "trace-input":
    save(a[3], { application: load(a[0]), seed: { kind: "string", value: a[1] }, direction: a[2] ?? "incoming" });
    break;

  case "trace-sum": {
    const r = load(a[0]).normalized_result;
    console.log(JSON.stringify(r.summary));
    for (const n of r.graph?.nodes ?? []) console.log("- " + label(n));
    break;
  }

  case "cmp-input":
    save(a[2], { left: load(a[0]), right: load(a[1]) });
    break;

  case "cmp-sum": {
    const r = load(a[0]).normalized_result;
    console.log("summary", JSON.stringify(r.summary));
    const nodes = new Map(r.graph.nodes.map((n) => [n.node_id, n]));
    for (const i of r.items.filter((x) => x.status === "changed"))
      console.log(`- [${i.dimensions.join(",")}] ${label(nodes.get(i.left_node_id))} → ${label(nodes.get(i.right_node_id))}`);
    break;
  }

  case "har-records":
    console.log(load(a[0]).log.entries.map((e, i) => (new URL(e.request.url).pathname.startsWith("/api/") ? `--record ${i}` : "")).filter(Boolean).join(" "));
    break;

  case "har-api": {
    const rows = new Map();
    for (const r of load(a[0]).normalized_result.records) {
      const q = r.reported.request, s = r.reported.response, u = new URL(q.url);
      if (!u.pathname.startsWith("/api/")) continue;
      const k = `${q.method} ${u.pathname.replace(/\/\d+(?=\/|$)/g, "/{id}")}`;
      const x = rows.get(k) ?? { n: 0, st: new Set(), qs: new Set(), req: new Set(), res: new Set() };
      x.n++; x.st.add(s.status); for (const p of u.searchParams.keys()) x.qs.add(p);
      try { Object.keys(JSON.parse(q.postData?.text ?? "x")).forEach((k2) => x.req.add(k2)); } catch {}
      try { const j = JSON.parse(s.content?.text ?? "x"); Object.keys(Array.isArray(j) ? j[0] ?? {} : j).forEach((k2) => x.res.add(k2)); } catch {}
      rows.set(k, x);
    }
    console.log("| endpoint | ครั้ง | status | query | request body keys | response keys |\n|---|---|---|---|---|---|");
    for (const [k, x] of rows) console.log(`| \`${k}\` | ${x.n} | ${[...x.st].join("/")} | ${[...x.qs].join(", ")} | ${[...x.req].join(", ")} | ${[...x.res].join(", ")} |`);
    break;
  }

  default:
    console.log("ดูวิธีใช้ที่หัวไฟล์ rea-tools.mjs");
}
