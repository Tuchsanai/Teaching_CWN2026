// rea-summarize.mjs — ย่อ Evidence JSON ก้อนใหญ่ของ REA ให้อ่านง่าย (ไม่ต้องมี jq)
// ใช้:  node rea\rea-summarize.mjs <evidence.json> [--md] [--all] [--samples] [--png <file>]
//       node rea\rea-summarize.mjs --s2b-table <a.json> <b.json> <c.json> <d.json>
// โหมด (เลือกจาก operation ในไฟล์): analyze_javascript_application · inspect_web_network_capture ·
//   trace_application_feature · compare_source_to_bundle · capture_browser_scenario ·
//   compare_application_versions · HistoricalSourceGraph (ผล import-reference-source)
// ค่าเริ่มต้นพิมพ์ JSON · --md = ตาราง Markdown · --all = ทุกแถว · --png = เขียนภาพสุดท้ายของ scenario
// --samples = (HAR/scenario) พิมพ์ body ตัวอย่างแบบย่อของ API (array เหลือ 1 ตัว · อีเมลถูกแทนด้วย <อีเมล> · body ที่ REA ปิดไว้ยังเป็น (redacted))
// key ของ HAR แสดง 2 ชั้น เช่น order{id,total,giftWrap} · method ของ endpoint ในผล analyze = helper อ่านจาก bundle ตรงตำแหน่งที่ REA ชี้ (REA ไม่ได้บันทึก method เอง)
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { basename, dirname, resolve } from "node:path";

const USAGE =
  "usage: node rea/rea-summarize.mjs <evidence.json> [--md] [--all] [--samples] [--png <file>]\n" +
  "       node rea/rea-summarize.mjs --s2b-table <a.json> <b.json> <c.json> <d.json>";
const usage = () => {
  console.error(USAGE);
  process.exit(2);
};

// ---------- argv ----------
const argv = process.argv.slice(2);
let md = false, all = false, png = null, s2bTable = false, samples = false;
const files = [];
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === "--md") md = true;
  else if (a === "--all") all = true;
  else if (a === "--samples") samples = true;
  else if (a === "--s2b-table") s2bTable = true;
  else if (a === "--png") {
    png = argv[++i];
    if (!png || png.startsWith("--")) usage();
  } else if (a.startsWith("--")) usage();
  else files.push(a);
}
if (s2bTable ? files.length !== 4 : files.length !== 1) usage();

const load = (file) => {
  let text;
  try {
    text = readFileSync(resolve(process.cwd(), file), "utf8");
  } catch (e) {
    console.error(`อ่านไฟล์ไม่ได้: ${file} (${e.code ?? e.message})`);
    process.exit(1);
  }
  try {
    return JSON.parse(text.replace(/^﻿/, ""));
  } catch (e) {
    console.error(`ไม่ใช่ JSON: ${file} (${e.message})`);
    process.exit(1);
  }
};

const shortId = (id) => (typeof id === "string" && id.startsWith("ev_") ? "ev_" + id.slice(3, 11) : id ?? null);
const count = (arr, key) => arr.reduce((m, x) => ((m[key(x)] = (m[key(x)] ?? 0) + 1), m), {});
const props = (n) => n?.observations?.[0]?.properties ?? {};
const label = (n) => n?.observations?.[0]?.label;
const cmp = (a, b) => (String(a) < String(b) ? -1 : String(a) > String(b) ? 1 : 0);
const cell = (v) => String(v ?? "-").replace(/\|/g, "\\|");
const S2B_CLASSES = ["unchanged", "modified", "removed", "split", "merged", "duplicated", "unknown"];
const s2bSummary = (nr) => Object.fromEntries(S2B_CLASSES.map((k) => [k, nr?.summary?.[k] ?? 0]));
const print = (s) => console.log(s);

// key 2 ชั้นของ JSON body: {"order":{"id":..,"giftWrap":..},"id":..} → ["order{id,giftWrap}", "id"] · array of object → items[]{slug,qty}
const parseJson = (txt) => {
  try {
    return JSON.parse(txt);
  } catch {
    return undefined;
  }
};
const isObj = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
const keyOf = (k, v) => {
  if (isObj(v)) return `${k}{${Object.keys(v).join(",")}}`;
  if (Array.isArray(v) && isObj(v[0])) return `${k}[]{${Object.keys(v[0]).join(",")}}`;
  return k;
};
const keys2 = (txt) => {
  const j = parseJson(txt);
  if (j === undefined || j === null || typeof j !== "object") return [];
  if (Array.isArray(j)) return [isObj(j[0]) ? `[]{${Object.keys(j[0]).join(",")}}` : "[array]"];
  return Object.entries(j).map(([k, v]) => keyOf(k, v));
};
// body ตัวอย่างแบบย่อ (ใช้กับ --samples): array เหลือตัวแรก + จำนวนที่ตัด · string ยาวถูกตัด · อีเมลถูกแทน
const EMAIL = /[^\s"'<>@]+@[^\s"'<>@]+\.[A-Za-z]{2,}/g;
const shrink = (v, depth = 0) => {
  if (typeof v === "string") return (v.length > 60 ? v.slice(0, 57) + "…" : v).replace(EMAIL, "<อีเมล>");
  if (Array.isArray(v)) {
    if (!v.length) return [];
    const head = depth > 2 ? "…" : shrink(v[0], depth + 1);
    return v.length > 1 ? [head, `…(+${v.length - 1})`] : [head];
  }
  if (isObj(v)) return depth > 2 ? "{…}" : Object.fromEntries(Object.entries(v).map(([k, x]) => [k, shrink(x, depth + 1)]));
  return v;
};
const sampleOf = (txt) => {
  if (txt == null || txt === "") return null;
  const j = parseJson(txt);
  const s = j === undefined ? String(txt).replace(EMAIL, "<อีเมล>") : JSON.stringify(shrink(j));
  return s.length > 400 ? s.slice(0, 397) + "…" : s;
};

// ---------- D′ --s2b-table ----------
if (s2bTable) {
  const evs = files.map((f) => ({ name: basename(f).replace(/\.json$/i, ""), file: basename(f), ev: load(f) }));
  for (const x of evs) {
    if (x.ev.operation !== "compare_source_to_bundle") {
      console.error(`${x.file} ไม่ใช่ผล compare_source_to_bundle (operation = ${x.ev.operation})`);
      process.exit(2);
    }
  }
  const maps = evs.map((x) => new Map((x.ev.normalized_result?.items ?? []).map((i) => [i.source_path, i.status])));
  const paths = [...new Set(maps.flatMap((m) => [...m.keys()]))].sort(cmp);
  print(`| source file | ${evs.map((x) => x.name).join(" | ")} |`);
  print(`|---|${evs.map(() => "---").join("|")}|`);
  for (const p of paths) {
    const st = maps.map((m) => m.get(p) ?? "(not in src)");
    if (st.every((s) => s === st[0])) continue;
    print(`| ${cell(p)} | ${st.join(" | ")} |`);
  }
  print("");
  for (const x of evs) print(`${x.file} ${JSON.stringify(s2bSummary(x.ev.normalized_result))}`);
  process.exit(0);
}

// ---------- single file ----------
const ev = load(files[0]);
const nr = ev.normalized_result ?? {};
const mode = ev.operation ?? (ev.schema === "HistoricalSourceGraph" ? "HistoricalSourceGraph" : undefined);
let out;
let mdLines = null;

if (mode === "analyze_javascript_application") {
  const g = nr.graph ?? { nodes: [], edges: [] };
  const nodes = g.nodes ?? [];
  const digest = ev.subject?.digest?.sha256 ?? null;
  // REA ไม่บันทึก HTTP method ของ endpoint → helper เปิดไฟล์ bundle (ถ้ามีบนเครื่อง: /work/... = โฟลเดอร์ปัจจุบัน)
  // แล้วอ่านช่วงตัวอักษรที่ REA ชี้ (บรรทัดเริ่ม 1 · คอลัมน์เริ่ม 0) หา method:"POST" · fetch ที่ไม่ระบุ method = GET (ค่าเริ่มต้นของ fetch)
  const inputDir = typeof nr.input_path === "string" && nr.input_path.startsWith("/work/") ? resolve(process.cwd(), nr.input_path.slice(6)) : null;
  const fileCache = new Map();
  const methodAt = (rel, loc, mechanism) => {
    if (!inputDir || !rel || !loc?.start || !loc?.end || !/fetch/.test(String(mechanism))) return null;
    if (!fileCache.has(rel)) {
      const f = resolve(inputDir, rel);
      fileCache.set(rel, existsSync(f) ? readFileSync(f, "utf8").split("\n") : null);
    }
    const lines = fileCache.get(rel);
    if (!lines) return null;
    const { start, end } = loc;
    const text =
      start.line === end.line
        ? (lines[start.line - 1] ?? "").slice(start.column, end.column)
        : [lines[start.line - 1]?.slice(start.column), ...lines.slice(start.line, end.line - 1), lines[end.line - 1]?.slice(0, end.column)].join("\n");
    const m = text.match(/method\s*:\s*["'`]([A-Za-z]+)["'`]/);
    if (m) return m[1].toUpperCase();
    return /method\s*:/.test(text) ? "?" : "GET";
  };
  const addMethod = (cur, m) => {
    if (m) cur.methods = [...new Set([...(cur.methods ?? []), m])].sort(cmp);
  };
  const epMap = new Map();
  for (const n of nodes.filter((n) => n.kind === "endpoint")) {
    const p = props(n);
    const k = JSON.stringify([p.value ?? null, p.mechanism ?? null]);
    const cur = epMap.get(k) ?? { value: p.value ?? null, mechanism: p.mechanism ?? null, count: 0 };
    cur.count++;
    const loc = n.observations?.[0]?.evidence?.location?.value;
    addMethod(cur, methodAt(loc?.source, loc, p.mechanism));
    epMap.set(k, cur);
  }
  // node "electron-renderer" = REA ตีความหน้า HTML ที่มี <script src> ว่าเป็น renderer (ชื่อ role จากโลก Electron) ไม่ได้แปลว่าแอปเป็น Electron
  const electron_renderer = nodes
    .filter((n) => n.kind === "electron-renderer")
    .map((n) => ({
      source: n.observations?.[0]?.evidence?.location?.value?.source ?? (String(n.identity?.key ?? "").replace(/^electron-renderer:[^:]*:/, "") || null),
      mechanism: props(n).mechanism ?? null,
      scripts: (n.observations ?? []).length,
    }))
    .sort((a, b) => cmp(a.source, b.source));
  const storage = nodes
    .filter((n) => n.kind === "storage")
    .map((n) => ({ kind: props(n).storage_kind ?? null, name: props(n).name ?? null, mechanism: props(n).mechanism ?? null }));
  // ไฟล์ที่ชนเพดานผลลัพธ์ของ REA (application_projection_failure) ไม่ถูกแตกเป็น node endpoint/storage
  // แต่ REA เก็บ fact ไว้ที่ node ของไฟล์ (static_analysis) → รวมมาด้วย และติดป้าย file_node = ชื่อไฟล์
  const retained_on_file_nodes = [];
  for (const n of nodes.filter((n) => n.kind === "javascript-asset")) {
    for (const ob of n.observations ?? []) {
      const p = ob.properties ?? {};
      if (!p.application_projection_failure || !p.static_analysis) continue;
      const file = ob.label ?? null;
      retained_on_file_nodes.push(file);
      for (const e of p.static_analysis.endpoints ?? []) {
        const k = JSON.stringify([e.value ?? null, e.mechanism ?? null, file]);
        const cur = epMap.get(k) ?? { value: e.value ?? null, mechanism: e.mechanism ?? null, count: 0, file_node: file };
        cur.count++;
        addMethod(cur, methodAt(file, e.location, e.mechanism));
        epMap.set(k, cur);
      }
      const seen = new Set();
      for (const s of p.static_analysis.storage ?? []) {
        const row = { kind: s.kind ?? null, name: s.name ?? null, mechanism: s.mechanism ?? null, file_node: file };
        const k = JSON.stringify(row);
        if (!seen.has(k)) storage.push(row), seen.add(k);
      }
    }
  }
  const endpoints = [...epMap.values()].sort((a, b) => cmp(a.value, b.value) || cmp(a.mechanism, b.mechanism));
  const recovered = [
    ...new Set(
      nodes
        .filter((n) => n.kind === "source-module")
        .map((n) => {
          const l = String(label(n) ?? "").replace(/^(\.\.\/)+/, "");
          try {
            return decodeURIComponent(l);
          } catch {
            return l;
          }
        })
        .filter((p) => /^(app|components|lib)\/.+\.(ts|tsx)$/.test(p) && !p.includes("/__nextjs-internal-proxy")),
    ),
  ].sort(cmp);
  out = {
    operation: ev.operation,
    evidence_id: ev.evidence_id,
    evidence_id_short: shortId(ev.evidence_id),
    input: nr.input_path ?? null,
    subject_digest: digest,
    subject_digest_short: digest ? digest.slice(0, 12) : null,
    files: nr.statistics?.relevant_files ?? null,
    node_kinds: count(nodes, (n) => n.kind),
    edges: (g.edges ?? []).length,
    coverage: { application: g.coverage?.status ?? null, semantic: nr.semantic_graph?.coverage?.status ?? null },
    endpoints,
    storage,
    electron_renderer,
    retained_on_file_nodes: retained_on_file_nodes.length,
    limitations: (nr.limitations ?? ev.limitations ?? []).length,
    recovered_source_files: recovered,
  };
  if (md) {
    const where = (x) => (x.file_node ? `file node \`${cell(x.file_node)}\`` : "graph node");
    const mth = (e) => (e.methods ? e.methods.join("/") : "-");
    mdLines = [
      `${out.evidence_id_short} · input ${out.input} · digest ${out.subject_digest_short} · files ${out.files} · edges ${out.edges} · coverage ${out.coverage.application}/${out.coverage.semantic} · limitations ${out.limitations}`,
      "",
      "| ชนิด node | จำนวน |",
      "|---|---|",
      ...Object.entries(out.node_kinds).map(([k, v]) => `| ${cell(k)} | ${v} |`),
      "",
      "| endpoint | mechanism | method (helper อ่าน bundle) | จำนวน | ที่มา |",
      "|---|---|---|---|---|",
      ...endpoints.map((e) => `| \`${cell(e.value)}\` | ${cell(e.mechanism)} | ${mth(e)} | ${e.count} | ${where(e)} |`),
      "",
      "| storage | name | mechanism | ที่มา |",
      "|---|---|---|---|",
      ...storage.map((s) => `| ${cell(s.kind)} | ${cell(s.name)} | ${cell(s.mechanism)} | ${where(s)} |`),
      "",
      ...(electron_renderer.length
        ? [
            "| electron-renderer (ไฟล์ HTML ที่ REA ตีความ · ไม่ใช่แอป Electron) | mechanism | จำนวน script |",
            "|---|---|---|",
            ...electron_renderer.map((r) => `| \`${cell(r.source)}\` | ${cell(r.mechanism)} | ${r.scripts} |`),
            "",
          ]
        : []),
      `recovered_source_files: ${recovered.length}`,
      ...(retained_on_file_nodes.length
        ? [`retained_on_file_nodes: ${retained_on_file_nodes.length} ไฟล์ (REA ชนเพดานผลลัพธ์ · fact ของไฟล์เหล่านี้เก็บไว้ที่ node ของไฟล์ ไม่ได้แตกเป็น node endpoint/storage · แถว "file node" ด้านบน)`]
        : []),
    ];
  }
} else if (mode === "inspect_web_network_capture") {
  const recs = nr.records ?? [];
  // --sensitive-value ทำให้ REA ลบ body ทั้งก้อน (text = null) → แสดง "(redacted)" แทน "-"
  const redacted = (x, pointer) => (x.redactions ?? []).some((r) => r.pointer === pointer);
  const api = recs
    .filter((x) => (x.reported ?? x)?.request?.url?.includes("/api/"))
    .map((x) => {
      const e = x.reported ?? x;
      const u = new URL(e.request.url);
      const reqRed = redacted(x, "/request/postData/text");
      const resRed = redacted(x, "/response/content/text");
      const row = {
        method: e.request.method,
        path: u.pathname + u.search,
        status: e.response?.status,
        req_keys: reqRed ? ["(redacted)"] : keys2(e.request.postData?.text ?? ""),
        res_keys: resRed ? ["(redacted)"] : keys2(e.response?.content?.text ?? ""),
      };
      if (samples) {
        row.req_sample = reqRed ? "(redacted)" : sampleOf(e.request.postData?.text);
        row.res_sample = resRed ? "(redacted)" : sampleOf(e.response?.content?.text);
      }
      return row;
    });
  out = { operation: ev.operation, evidence_id_short: shortId(ev.evidence_id), records: recs.length, api };
  if (md) {
    mdLines = [
      `${out.evidence_id_short} · records ${out.records} · API ${api.length}`,
      "",
      "| # | method | path | status | request body keys | response keys |",
      "|---|---|---|---|---|---|",
      ...api.map((a, i) => `| ${i + 1} | ${a.method} | \`${a.path}\` | ${a.status} | ${cell(a.req_keys.join(", ") || "-")} | ${cell(a.res_keys.join(", ") || "-")} |`),
      ...(samples
        ? ["", "ตัวอย่าง body (ย่อ · array เหลือตัวแรก):", ...api.flatMap((a, i) => [`- #${i + 1} ${a.method} ${a.path} request: \`${a.req_sample ?? "-"}\``, `  response: \`${a.res_sample ?? "-"}\``])]
        : []),
    ];
  }
} else if (mode === "trace_application_feature") {
  const nodes = (nr.graph?.nodes ?? [])
    .map((n) => ({
      kind: n.kind,
      label: label(n) ?? null,
      path: n.observations?.[0]?.evidence?.location?.value?.path ?? null,
    }))
    .sort((a, b) => cmp(a.kind, b.kind) || cmp(a.label, b.label));
  const sumKeys = ["matched_seeds", "traced_nodes", "traced_edges", "terminal_paths", "native_handoffs", "observed_facts", "inferred_facts", "unknown_facts", "unavailable_facts"];
  const source_files = [
    ...new Set((nr.graph?.nodes ?? []).filter((n) => n.kind === "source-module").map((n) => String(label(n) ?? "").replace(/^(\.\.\/)+/, ""))),
  ].sort(cmp);
  out = {
    operation: ev.operation,
    evidence_id_short: shortId(ev.evidence_id),
    source_evidence_id: nr.source_evidence_id ?? null,
    seed: { kind: nr.seed?.kind ?? null, value: nr.seed?.value ?? null },
    direction: nr.direction ?? null,
    summary: Object.fromEntries(sumKeys.map((k) => [k, nr.summary?.[k] ?? null])),
    coverage: nr.coverage?.status ?? null,
    nodes,
    source_files,
  };
  if (md) {
    mdLines = [
      `${out.evidence_id_short} · seed ${out.seed.kind}:${out.seed.value} · ${out.direction} · coverage ${out.coverage}`,
      `summary: ${sumKeys.map((k) => `${k} ${out.summary[k]}`).join(" · ")}`,
      "",
      "| kind | label |",
      "|---|---|",
      ...nodes.map((n) => `| ${cell(n.kind)} | ${cell(n.label)} |`),
      "",
      `source_files: ${source_files.join(", ") || "-"}`,
    ];
  }
} else if (mode === "compare_source_to_bundle") {
  const summary = s2bSummary(nr);
  const items = (nr.items ?? [])
    .filter((i) => all || i.status !== "unchanged")
    .map((i) => ({ source_path: i.source_path, status: i.status, confidence: i.confidence ?? null }))
    .sort((a, b) => cmp(a.source_path, b.source_path));
  out = { operation: ev.operation, evidence_id_short: shortId(ev.evidence_id), summary, items };
  if (md) {
    mdLines = [
      `${out.evidence_id_short} · ${S2B_CLASSES.map((k) => `${k} ${summary[k]}`).join(" · ")}`,
      "",
      "| source_path | status | confidence |",
      "|---|---|---|",
      ...items.map((i) => `| ${cell(i.source_path)} | ${i.status} | ${cell(i.confidence)} |`),
    ];
  }
} else if (mode === "capture_browser_scenario") {
  const steps = nr.steps ?? [];
  const last = steps.at(-1);
  const art = last?.artifacts ?? {};
  const st = art.storage?.value ?? {};
  // รวมคู่ "term: ยอดชำระทั้งหมด" + "definition: ฿113" เป็นบรรทัดเดียว เพื่อไม่ให้ป้ายของตัวเลขหลุด
  const rawA11y = String(art.accessibility?.value?.text ?? "")
    .split(/\r?\n/)
    .map((l) => l.trim());
  const merged = [];
  for (let i = 0; i < rawA11y.length; i++) {
    const t = rawA11y[i].match(/^- term: (.*)$/);
    const d = rawA11y[i + 1]?.match(/^- definition: (.*)$/);
    if (t && d) merged.push(`- ${t[1]} = ${d[1].replace(/^"(.*)"$/, "$1")}`), i++;
    else merged.push(rawA11y[i]);
  }
  const a11y = merged.filter((l) => l && (l.includes("฿") || l.includes("คูปอง") || l.includes("PAW"))).slice(0, 40);
  const items = nr.events?.items ?? [];
  const bodyOf = (tid, phase) => {
    const c = items.find((e) => e.kind === "network-content" && e.transaction_id === tid && e.phase === phase && e.body?.state === "captured");
    return c ? Buffer.from(c.body.content ?? "", c.body.encoding === "base64" ? "base64" : "utf8").toString("utf8") : null;
  };
  const api_calls = items
    .filter((e) => e.kind === "request" && String(e.url?.url ?? "").includes("/api/"))
    .map((rq) => {
      const rs = items.find((e) => e.kind === "response" && e.transaction_id === rq.transaction_id);
      return {
        method: rq.method,
        path: new URL(rq.url.url).pathname,
        status: rs?.status ?? null,
        request_body: bodyOf(rq.transaction_id, "request"),
        response_body: bodyOf(rq.transaction_id, "response"),
      };
    });
  const done = steps.filter((s) => s.status === "completed").length;
  out = {
    operation: ev.operation,
    evidence_id_short: shortId(ev.evidence_id),
    duration_ms: nr.duration_ms ?? null,
    completeness: { status: nr.completeness?.status ?? null, missing_sections: nr.completeness?.missing_sections ?? [] },
    steps: steps.map((s) => ({ step_id: s.step_id, status: s.status, elapsed_ms: s.elapsed_ms, after_url: s.after_url?.url ?? null })),
    steps_completed: `${done}/${steps.length}`,
    local_storage_keys: (st.local_storage ?? []).map((x) => x.name),
    session_storage_keys: (st.session_storage ?? []).map((x) => x.name),
    cookies: (st.cookies ?? []).length,
    a11y_lines: a11y,
    api_calls,
  };
  if (png) {
    const data = art.screenshot?.value?.data_base64;
    if (!data) {
      console.error("ขั้นสุดท้ายไม่มี screenshot (artifacts.screenshot.value.data_base64)");
      process.exit(1);
    }
    const buf = Buffer.from(data, "base64");
    const target = resolve(process.cwd(), png);
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, buf);
    print(`png: ${png} (${buf.length} bytes)`);
  }
  if (md) {
    mdLines = [
      `${out.evidence_id_short} · steps_completed ${out.steps_completed} · ${out.duration_ms} ms · completeness ${out.completeness.status}` +
        (out.completeness.missing_sections.length ? ` (missing: ${out.completeness.missing_sections.join(", ")})` : ""),
      "",
      "| step | status | ms | url |",
      "|---|---|---|---|",
      ...out.steps.map((s) => `| ${cell(s.step_id)} | ${s.status} | ${s.elapsed_ms} | ${cell(s.after_url)} |`),
      "",
      `local_storage_keys: ${out.local_storage_keys.join(", ") || "-"} · session_storage_keys: ${out.session_storage_keys.join(", ") || "-"} · cookies: ${out.cookies}`,
      "",
      "a11y:",
      ...a11y.map((l) => (l.startsWith("- ") ? l : `- ${l}`)),
      "",
      "| method | path | status | request body keys | response keys |",
      "|---|---|---|---|---|",
      ...api_calls.map((c) => `| ${c.method} | \`${c.path}\` | ${c.status} | ${cell(keys2(c.request_body ?? "").join(", ") || "-")} | ${cell(keys2(c.response_body ?? "").join(", ") || "-")} |`),
      ...(samples
        ? ["", "ตัวอย่าง body (ย่อ · array เหลือตัวแรก):", ...api_calls.flatMap((c) => [`- ${c.method} ${c.path} request: \`${sampleOf(c.request_body) ?? "-"}\``, `  response: \`${sampleOf(c.response_body) ?? "-"}\``])]
        : []),
    ];
  }
} else if (mode === "compare_application_versions") {
  const items = nr.items ?? [];
  const byId = new Map((nr.graph?.nodes ?? []).map((n) => [n.node_id, n]));
  const lab = (id) => (id && label(byId.get(id))) ?? id ?? null;
  const by_kind_status = {};
  for (const i of items) {
    const k = i.node_kind ?? "unknown";
    by_kind_status[k] ??= {};
    by_kind_status[k][i.status] = (by_kind_status[k][i.status] ?? 0) + 1;
  }
  const changed = items.filter((i) => i.status !== "unchanged");
  const sample = (all ? changed : changed.slice(0, 20)).map((i) => ({
    status: i.status,
    node_kind: i.node_kind,
    label: lab(i.left_node_id) ?? lab(i.right_node_id),
  }));
  const sk = ["unchanged", "added", "removed", "changed", "unknown"];
  out = {
    operation: ev.operation,
    evidence_id_short: shortId(ev.evidence_id),
    summary: Object.fromEntries(sk.map((k) => [k, nr.summary?.[k] ?? 0])),
    items_total: items.length,
    by_kind_status,
    sample,
  };
  if (md) {
    mdLines = [
      `${out.evidence_id_short} · ${sk.map((k) => `${k} ${out.summary[k]}`).join(" · ")} · items_total ${out.items_total}`,
      "",
      "| node_kind | status | จำนวน |",
      "|---|---|---|",
      ...Object.entries(by_kind_status).flatMap(([k, m]) => Object.entries(m).map(([s, n]) => `| ${cell(k)} | ${s} | ${n} |`)),
    ];
  }
} else if (mode === "HistoricalSourceGraph") {
  out = {
    schema: ev.schema,
    root_sha256_short: typeof ev.root_sha256 === "string" ? ev.root_sha256.slice(0, 12) : null,
    entries: (ev.entries ?? []).length,
    languages: ev.languages ?? [],
    inventory_state: ev.inventory_state ?? null,
  };
  if (md) {
    mdLines = [
      "| schema | root_sha256 | entries | languages | inventory_state |",
      "|---|---|---|---|---|",
      `| ${out.schema} | ${out.root_sha256_short} | ${out.entries} | ${out.languages.join(", ")} | ${out.inventory_state} |`,
    ];
  }
} else {
  out = { operation: ev.operation ?? null, evidence_id_short: shortId(ev.evidence_id), keys: Object.keys(nr) };
}

print(mdLines ? mdLines.join("\n") : JSON.stringify(out, null, 2));
