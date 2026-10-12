// peek structure of REA har.json (keys only + api record samples), never prints secrets
import { readFileSync } from "node:fs";
const j = JSON.parse(readFileSync(process.argv[2], "utf8"));
const mode = process.argv[3] ?? "keys";
const shape = (o, d = 0) => {
  if (Array.isArray(o)) return `[${o.length}] ` + (o.length ? shape(o[0], d + 1) : "");
  if (o && typeof o === "object") return d > 3 ? "{…}" : "{" + Object.keys(o).map(k => k + ":" + shape(o[k], d + 1)).join(", ") + "}";
  return typeof o;
};
if (mode === "keys") console.log(shape(j).slice(0, 4000));
const recs = j.normalized_result.records;
if (mode === "rec") {
  const r = recs.find(r => JSON.stringify(r.reported).includes("/api/coupons"));
  console.log(shape(r.reported).slice(0, 3000));
}
if (mode === "red") {
  let n = 0; const kinds = {};
  for (const r of recs) for (const x of r.redactions) { n++; const k = JSON.stringify(x).slice(0, 120); kinds[k] = (kinds[k] ?? 0) + 1; }
  console.log("records", recs.length, "redactions", n, "sensitive_value_count", j.parameters.sensitive_value_count);
  console.log(Object.entries(kinds).slice(0, 10));
  console.log("limitations", j.limitations, j.normalized_result.limitations);
  console.log("redact top", j.normalized_result.container.redactions.length);
}
if (mode === "api") {
  for (const r of recs) {
    const q = r.reported.request; const u = new URL(q.url);
    if (!u.pathname.startsWith("/api/")) continue;
    const pd = q.postData?.text ?? ""; const rt = r.reported.response.content.text ?? "";
    console.log("==", q.method, u.pathname + u.search, r.reported.response.status, r.reported.response.content.mimeType, "time", Math.round(r.reported.time), "ms page", r.reported.pageref);
    console.log("  req:", pd.slice(0, 600));
    console.log("  res:", rt.slice(0, 900));
  }
}
if (mode === "types") {
  const t = {}; const pages = {};
  for (const r of recs) { const k = r.reported._resourceType; t[k] = (t[k] ?? 0) + 1; const u = new URL(r.reported.request.url); if (r.reported._resourceType === "document" || u.searchParams.has("_rsc")) { pages[r.reported.request.method + " " + u.pathname + (u.searchParams.has("_rsc") ? " (RSC)" : "") + " " + r.reported.response.status] = (pages[r.reported.request.method + " " + u.pathname + (u.searchParams.has("_rsc") ? " (RSC)" : "") + " " + r.reported.response.status] ?? 0) + 1; } }
  console.log(t); console.log(pages);
}
if (mode === "ref") {
  for (const r of recs) { const q = r.reported.request; const u = new URL(q.url); if (!u.pathname.startsWith("/api/")) continue;
    const ref = q.headers.find(h => h.name.toLowerCase() === "referer")?.value; const ct = q.headers.find(h => h.name.toLowerCase() === "content-type")?.value;
    let tot = ""; try { const b = JSON.parse(r.reported.response.content.text); if (b.total !== undefined && b.items) tot = "items=" + b.items.length + " total=" + b.total; } catch {}
    console.log(q.method, u.pathname, "referer=", ref, "ct=", ct, tot, "resHeaders=", r.reported.response.headers.map(h => h.name).join(","), "start", r.reported.startedDateTime); }
}
