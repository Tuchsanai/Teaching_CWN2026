// rea-summarize.mjs — ย่อ Evidence JSON ก้อนใหญ่ของ REA ให้อ่านง่าย (ไม่ต้องมี jq)
// ใช้:  node rea-summarize.mjs <evidence.json> [--md]
// รองรับ: analyze-javascript-application, inspect-web-network-capture, trace-application-feature,
//         compare-application-versions, capture-browser-scenario
import { readFileSync } from "node:fs";

const [, , file, flag] = process.argv;
if (!file) {
  console.error("usage: node rea-summarize.mjs <evidence.json> [--md]");
  process.exit(2);
}
const ev = JSON.parse(readFileSync(file, "utf8"));
const op = ev.operation;
const r = ev.normalized_result ?? {};
const out = { operation: op, evidence_id: ev.evidence_id };
const count = (arr, key) => arr.reduce((m, x) => ((m[key(x)] = (m[key(x)] ?? 0) + 1), m), {});
const obsValue = (n) => n.observations?.[0]?.properties ?? {};

if (op === "analyze_javascript_application") {
  const g = r.graph;
  out.input = r.input_path;
  out.files = r.statistics?.relevant_files;
  out.node_kinds = count(g.nodes, (n) => n.kind);
  out.edges = g.edges.length;
  out.coverage = { application: g.coverage?.status, semantic: r.semantic_graph?.coverage?.status };
  out.endpoints = g.nodes
    .filter((n) => n.kind === "endpoint")
    .map((n) => ({ value: obsValue(n).value, mechanism: obsValue(n).mechanism }))
    .sort((a, b) => String(a.value).localeCompare(String(b.value)));
  out.storage = g.nodes
    .filter((n) => n.kind === "storage")
    .map((n) => ({ kind: obsValue(n).storage_kind, name: obsValue(n).name, mechanism: obsValue(n).mechanism }));
  out.limitations = (r.limitations ?? ev.limitations ?? []).length;
} else if (op === "inspect_web_network_capture") {
  const recs = r.records ?? [];
  out.records = recs.length;
  out.api = recs
    .map((x) => x.reported ?? x)
    .filter((e) => e?.request?.url?.includes("/api/"))
    .map((e) => {
      const u = new URL(e.request.url);
      const keys = (txt) => {
        try {
          const j = JSON.parse(txt);
          return Array.isArray(j) ? ["[array]"] : Object.keys(j);
        } catch {
          return [];
        }
      };
      return {
        method: e.request.method,
        path: u.pathname + u.search,
        status: e.response?.status,
        req_keys: keys(e.request.postData?.text ?? ""),
        res_keys: keys(e.response?.content?.text ?? ""),
      };
    });
} else if (op === "compare_application_versions") {
  out.summary = r.summary;
  out.changed = (r.items ?? r.changes ?? [])
    .filter((i) => i.status && i.status !== "unchanged")
    .map((i) => ({ status: i.status, kind: i.kind ?? i.entity_kind, label: i.label ?? i.left?.label ?? i.right?.label, dims: i.changed_dimensions }));
} else {
  out.keys = Object.keys(r);
}

if (flag === "--md" && out.api) {
  console.log("| # | method | path | status | request body keys | response keys |");
  console.log("|---|---|---|---|---|---|");
  out.api.forEach((a, i) =>
    console.log(`| ${i + 1} | ${a.method} | \`${a.path}\` | ${a.status} | ${a.req_keys.join(", ") || "-"} | ${a.res_keys.join(", ") || "-"} |`),
  );
} else {
  console.log(JSON.stringify(out, null, 2));
}
