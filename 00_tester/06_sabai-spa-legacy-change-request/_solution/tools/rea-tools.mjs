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
//   node rea-tools.mjs shot        <scenario-out.json> <out.png>                  ดึงภาพหน้าจอสุดท้ายที่ REA ถ่ายใน capture-browser-scenario
//   node rea-tools.mjs ids         <ไฟล์หรือโฟลเดอร์ ...>                          ป้าย [E ev_xxxxxxxx] + ขนาด ของ Evidence ทุกไฟล์ (โฟลเดอร์ = ทุก .json/.har ในนั้น)
//   node rea-tools.mjs summary     <static.json | summary.json>                   สถิติของ analyze: node ตามชนิด · endpoint · statistics · coverage · limitations
//   node rea-tools.mjs scenario-sum <scenario-out.json> [regex data-testid]       step completed x/y · URL สุดท้าย · API ที่เรียก · ข้อความสำคัญในหน้าสุดท้าย (เช่นยอดรวม)
//   node rea-tools.mjs pages       <static.json> [static-v2.json]                 หน้า (route) จากชื่อไฟล์ chunks/app/**/page-*.js (+ เทียบสองเวอร์ชัน)
import { readFileSync, writeFileSync, statSync, readdirSync } from "node:fs";
import { createHash } from "node:crypto";
import { join, basename } from "node:path";

const [cmd, ...a] = process.argv.slice(2);
const load = (p) => JSON.parse(readFileSync(p, "utf8"));
const save = (p, o) => writeFileSync(p, JSON.stringify(o));
const short = (id) => (id ? `ev_${String(id).replace(/^ev_/, "").slice(0, 8)}` : "?");
const count = (xs, f) => xs.reduce((m, x) => m.set(f(x), (m.get(f(x)) ?? 0) + 1), new Map());
const pagesOf = (ev) => {
  // route ของหน้า ← ชื่อไฟล์ chunks/app/<route>/page-<hash>.js (layout แยกไว้ · route-*.js คือ API ดูด้วย endpoints)
  const g = ev.normalized_result.graph, out = new Map();
  for (const n of g.nodes) for (const o of n.observations ?? []) {
    const m = /^chunks\/app\/(?:(.*)\/)?(page|layout)-([0-9a-f]+)\.js$/.exec(o.properties?.path ?? "");
    if (m) out.set(m[2] === "layout" ? "(layout)" : "/" + (m[1] ?? ""), { file: o.properties.path, hash: m[3], fetch: new Set() });
  }
  for (const n of g.nodes.filter((x) => x.kind === "endpoint")) for (const o of n.observations) {
    const src = o.evidence?.location?.value?.source;
    for (const p of out.values()) if (p.file === src) p.fetch.add(o.properties.value);
  }
  return new Map([...out].sort(([a], [b]) => (a < b ? -1 : 1)));
};
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

  case "shot": {
    // ภาพ PNG (base64) ตัวสุดท้ายใน Evidence ของ capture-browser-scenario → ไฟล์ .png
    let last = null;
    const walk = (v) => {
      if (typeof v === "string") {
        const m = v.match(/^(?:data:image\/png;base64,)?(iVBORw0KGgo[A-Za-z0-9+/=]+)$/);
        if (m) last = m[1];
      } else if (v && typeof v === "object") for (const x of Object.values(v)) walk(x);
    };
    walk(load(a[0]));
    if (!last) { console.error("ไม่พบภาพ PNG ใน Evidence นี้"); process.exit(1); }
    const buf = Buffer.from(last, "base64");
    writeFileSync(a[1], buf);
    console.log(`เขียน ${a[1]} (${buf.length} bytes)`);
    break;
  }

  case "ids": {
    // ป้าย [E ev_xxxxxxxx] = evidence_id 8 ตัวแรก · ไฟล์ที่ไม่ใช่ Evidence (HAR ดิบ, input ของ view, ภาพ) ใช้ชื่อไฟล์ + sha256 ย่อแทน
    const files = a.flatMap((p) => (statSync(p).isDirectory()
      ? readdirSync(p).filter((f) => /\.(json|har)$/i.test(f)).sort().map((f) => join(p, f)) : [p]));
    console.log("| ไฟล์ | ขนาด (byte) | operation | ป้ายแหล่ง | หมายเหตุ |\n|---|---|---|---|---|");
    for (const f of files) {
      const buf = readFileSync(f);
      let j = null; try { j = JSON.parse(buf.toString("utf8")); } catch {}
      const sha = `sha256 ${createHash("sha256").update(buf).digest("hex").slice(0, 8)}`;
      let op = "-", tag = `[E ${basename(f)} ${sha}]`, note = "ไม่ใช่ Evidence";
      if (j?.evidence_id) {
        const nr = j.normalized_result ?? {};
        op = j.operation; tag = `[E ${short(j.evidence_id)}]`;
        note = nr.parent_evidence_id ? `view ของ ${short(nr.parent_evidence_id)}`
          : nr.total_records != null ? `records ${nr.records?.length ?? "?"}/${nr.total_records}`
          : nr.completeness ? `completeness ${nr.completeness.status} · ${nr.duration_ms} ms`
          : nr.graph?.coverage ? `coverage ${nr.graph.coverage.status}` : "";
      } else if (j?.source?.evidence) [tag, note] = ["-", `input ของ inspect-analysis-view (จาก ${short(j.source.evidence.evidence_id)})`];
      else if (j?.log?.entries) note = `HAR ดิบ ${j.log.entries.length} entries`;
      else if (j && "left" in j && "right" in j) [tag, note] = ["-", "input ของ compare-application-versions"];
      console.log(`| ${basename(f)} | ${buf.length.toLocaleString("en-US")} | ${op} | ${tag} | ${note} |`);
    }
    break;
  }

  case "summary": {
    // รับได้ทั้งผล analyze-javascript-application (static-v1.json) และผล inspect-analysis-view --format json (summary-v1.json)
    const ev = load(a[0]), nr = ev.normalized_result, isView = ev.operation === "inspect_analysis_view";
    if (!["analyze_javascript_application", "inspect_analysis_view"].includes(ev.operation)) {
      console.log(`${ev.operation} [E ${short(ev.evidence_id)}] — ไม่ใช่ผล analyze · ใช้ har-api / scenario-sum / cmp-sum / trace-sum แทน`);
      break;
    }
    const s = isView ? nr.summary : nr;
    const app = isView ? s.coverage.application : nr.graph.coverage;
    const sem = isView ? s.coverage.semantic : nr.semantic_graph.coverage;
    console.log(`## ${ev.operation} [E ${short(ev.evidence_id)}]${isView ? ` (view ของ ${short(nr.parent_evidence_id)})` : ""}`);
    console.log(`input ${s.input_path} · ${s.format} · root sha256 ${String(s.root_artifact_sha256).slice(0, 8)}`);
    if (!isView) {
      const g = nr.graph;
      console.log("\n| ชนิด node | จำนวน |\n|---|---|");
      for (const [k, v] of [...count(g.nodes, (n) => n.kind)].sort((x, y) => y[1] - x[1])) console.log(`| ${k} | ${v} |`);
      console.log(`| (edges) | ${g.edges.length} |`);
      const ep = g.nodes.filter((n) => n.kind === "endpoint").flatMap((n) => n.observations.map((o) => o.properties.value));
      const api = [...new Set(ep.filter((v) => v.startsWith("/api/")))].sort(), other = ep.filter((v) => !v.startsWith("/api/"));
      console.log(`\nendpoint ที่เห็น ${ep.length} จุด · /api/* ไม่ซ้ำ **${api.length}**: ${api.join(" ")}`);
      console.log(`อื่น ๆ ${other.length} จุด (ไม่ใช่ /api/ หรือชื่อที่ REA ประกอบไม่ได้): ${other.join(" ")}`);
    } else console.log("(view summary ไม่มี graph → นับ node/endpoint ด้วย: node tools\\rea-tools.mjs summary <static.json>)");
    console.log("\n| statistics | ค่า |\n|---|---|");
    for (const [k, v] of Object.entries(s.statistics)) console.log(`| ${k} | ${v} |`);
    const appUnk = isView ? s.coverage.application_unknowns : nr.graph.nodes.filter((n) => n.kind === "unknown").length;
    const semUnk = isView ? s.coverage.semantic_unknowns : nr.semantic_graph.unknowns.length;
    console.log(`\ncoverage: application **${app.status}** (truncated ${app.truncated}) · semantic **${sem.status}** (truncated ${sem.truncated}) · unknown: application ${appUnk} · semantic ${semUnk}`);
    if (isView) console.log(`view: ${nr.coverage.status} · examined ${nr.coverage.examined}/${nr.coverage.total}`);
    console.log("\n| semantic family | status | retained | unknown |\n|---|---|---|---|");
    for (const f of sem.families ?? []) console.log(`| ${f.family} | ${f.status} | ${f.retained_relations} | ${f.unknown_count ?? f.unknown_ids?.length ?? "?"} |`);
    const perFile = ev.limitations.filter((l) => /^[^ ]+\.js: Resource constraint/.test(l)).length;
    console.log(`\nlimitations: ${ev.limitations.length} ใน Evidence นี้ (รายไฟล์ที่ติด resource constraint ${perFile})${isView ? ` · limitation_count ของ parent = ${s.limitation_count}` : ""}`);
    console.log("อ่านว่า: partial = หลักฐานไม่ครบ → \"ไม่พบในหลักฐานนี้\" ≠ \"ระบบไม่มี\"");
    break;
  }

  case "scenario-sum": {
    // สรุป capture-browser-scenario โดยไม่ต้องเปิดไฟล์ (มีภาพ base64 + DOM ทั้งหน้า)
    const ev = load(a[0]), nr = ev.normalized_result, re = new RegExp(a[1] ?? "total|summary-service|summary-when");
    const rel = (u) => { try { const x = new URL(u); return x.pathname + x.search; } catch { return u ?? "-"; } };
    const done = nr.steps.filter((s) => s.status === "completed").length;
    console.log(`## capture-browser-scenario [E ${short(ev.evidence_id)}] · ${nr.browser?.product ?? ""} ${nr.browser?.version ?? ""} · ${nr.duration_ms} ms · completeness ${nr.completeness?.status}`);
    console.log(`\n**step completed ${done}/${nr.steps.length}** (scenario_start + ${nr.scenario?.action_count ?? "?"} action)\n`);
    console.log("| # | step_id | action | status | ms | URL หลัง step |\n|---|---|---|---|---|---|");
    for (const s of nr.steps) console.log(`| ${s.step_index} | ${s.step_id} | ${s.action} | ${s.status}${s.error ? " ⚠️ " + JSON.stringify(s.error).slice(0, 120) : ""} | ${s.elapsed_ms} | ${rel(s.after_url?.url)} |`);
    const last = nr.steps.at(-1);
    console.log(`\nURL สุดท้าย: ${last?.after_url?.url ?? "-"}`);
    const resp = (nr.events?.items ?? []).filter((e) => e.kind === "response" && /\/api\//.test(e.url?.url ?? ""));
    console.log(`\n| API ที่หน้าเว็บเรียก (method) | path | status | step |\n|---|---|---|---|`);
    for (const e of resp) console.log(`| ${e.method} | ${rel(e.url.url)} | ${e.status} | ${e.step_index} |`);
    // ข้อความสำคัญจาก DOM สุดท้าย: element ที่ data-testid ตรง regex → data-amount + ข้อความ (ตัด tag)
    const dom = [...nr.steps].reverse().find((s) => s.artifacts?.dom?.state === "captured")?.artifacts.dom.value.text ?? "";
    console.log(`\n| ข้อความในหน้าสุดท้าย (data-testid ~ /${re.source}/) | data-amount | ข้อความ |\n|---|---|---|`);
    for (const m of dom.matchAll(/<([a-zA-Z0-9]+)\b([^>]*\bdata-testid="([^"]+)"[^>]*)>/g)) {
      if (!re.test(m[3])) continue;
      const tag = m[1].toLowerCase(), open = new RegExp(`<${tag}\\b|</${tag}>`, "gi");
      open.lastIndex = m.index + m[0].length;
      let depth = 1, end = dom.length, t;
      while (depth && (t = open.exec(dom))) { depth += t[0].startsWith("</") ? -1 : 1; if (!depth) end = t.index; }
      const text = dom.slice(m.index + m[0].length, end).replace(/<[^>]+>/g, " ").replace(/&nbsp;/g, " ").replace(/\s+/g, " ").trim();
      console.log(`| ${m[3]} | ${/data-amount="([^"]*)"/.exec(m[2])?.[1] ?? ""} | ${text.slice(0, 80)} |`);
    }
    const ax = last?.artifacts?.accessibility;
    console.log(`\naccessibility: ${ax?.state ?? "-"}${ax?.state === "captured" ? "" : " (scenario ไม่ได้ขอ → ข้อความข้างบนมาจาก DOM สุดท้าย)"} · screenshot: ${last?.artifacts?.screenshot?.state ?? "-"} (ดึงภาพด้วยคำสั่ง shot)`);
    break;
  }

  case "pages": {
    // หน้า (route) ที่เห็นจากชื่อไฟล์ใน bundle · ใส่สองไฟล์ = เทียบ v1/v2 (hash ในชื่อไฟล์เปลี่ยน = เนื้อไฟล์เปลี่ยน)
    const [p1, p2] = [a[0], a[1]].map((f) => f && pagesOf(load(f)));
    const show = (s) => [...s].join(" ") || "-";
    if (!p2) {
      console.log("| route | ไฟล์ใน bundle | fetch ที่ REA เห็นในไฟล์นี้ |\n|---|---|---|");
      for (const [r, p] of p1) console.log(`| \`${r}\` | ${p.file} | ${show(p.fetch)} |`);
      console.log(`\nหน้า ${[...p1.keys()].filter((r) => r.startsWith("/") && r !== "/_not-found").length} route + /_not-found + layout · API route ดูด้วยคำสั่ง endpoints`);
      console.log(`"-" = REA ไม่เห็น fetch ที่ URL เป็นค่าคงที่ในไฟล์นี้ (ไม่ได้แปลว่าหน้านี้ไม่เรียก API: URL ที่ประกอบตอนรัน หรือข้อมูลที่อ่านฝั่งเซิร์ฟเวอร์ จะไม่โผล่)`);
    } else {
      console.log("| route | v1 hash | v2 hash | สถานะ |\n|---|---|---|---|");
      for (const r of [...new Set([...p1.keys(), ...p2.keys()])].sort()) {
        const x = p1.get(r), y = p2.get(r);
        const st = !x ? "ใหม่ใน v2" : !y ? "หายใน v2" : x.hash === y.hash ? "เหมือนเดิม" : "ไฟล์เปลี่ยน (hash ต่าง)";
        console.log(`| \`${r}\` | ${x?.hash.slice(0, 8) ?? "-"} | ${y?.hash.slice(0, 8) ?? "-"} | ${st} |`);
      }
    }
    break;
  }

  default:
    console.log("ดูวิธีใช้ที่หัวไฟล์ rea-tools.mjs");
}
