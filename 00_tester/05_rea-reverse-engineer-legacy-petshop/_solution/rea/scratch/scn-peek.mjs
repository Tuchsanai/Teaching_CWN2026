// peek REA scenario evidence: top-level shape, completeness, a11y lines containing a word, network summary
import { readFileSync } from "node:fs";
const j = JSON.parse(readFileSync(process.argv[2], "utf8"));
const mode = process.argv[3] ?? "keys";
const shape = (o, d = 0) => Array.isArray(o) ? `[${o.length}] ` + (o.length ? shape(o[0], d + 1) : "") : (o && typeof o === "object") ? (d > 2 ? "{…}" : "{" + Object.keys(o).map(k => k + ":" + shape(o[k], d + 1)).join(", ") + "}") : typeof o;
if (mode === "keys") console.log(shape(j.normalized_result ?? j).slice(0, 3000));
if (mode === "grep") { const s = JSON.stringify(j); const re = new RegExp(process.argv[4], "g"); let m, n = 0; while ((m = re.exec(s)) && n < 12) { n++; console.log(s.slice(Math.max(0, m.index - 140), m.index + 160).replace(/\n/g, " | ")); console.log("--"); } console.log("hits(≤12 shown)", n); }
