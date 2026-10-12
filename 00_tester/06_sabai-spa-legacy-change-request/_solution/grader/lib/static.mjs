// ตรวจแบบไม่ต้องเปิดระบบ: git · แยกเคสใน check-rules / e2e-legacy · ORACLE-CHANGES · ข้อ 1 · ข้อ 3
import { sh } from "./sh.mjs";

// ───────────── git ─────────────
export async function git(repo, args, o = {}) {
  const r = await sh("git", ["-c", "core.autocrlf=false", "-c", "core.quotepath=false", "-C", repo, ...args], o);
  return r;
}
export async function show(repo, commit, path) {
  if (!commit) return null;
  const r = await git(repo, ["show", `${commit}:${path}`]);
  return r.code === 0 ? r.out : null;
}
export async function lsFiles(repo, commit, path) {
  if (!commit) return [];
  const r = await git(repo, ["ls-tree", "-r", "--name-only", commit, "--", path]);
  return r.code === 0 ? r.out.split("\n").map((s) => s.trim()).filter(Boolean) : [];
}
export async function changedFiles(repo, a, b, paths = []) {
  if (!a || !b) return [];
  const r = await git(repo, ["diff", "--name-only", a, b, "--", ...paths]);
  return r.code === 0 ? r.out.split("\n").map((s) => s.trim()).filter(Boolean) : [];
}
export async function treeHash(repo, commit, path) {
  const r = await git(repo, ["rev-parse", `${commit}:${path}`]);
  return r.code === 0 ? r.out.trim() : null;
}

/** commit EX0…EX8 / EX5-red จากข้อความ commit (ใช้ commit สุดท้ายที่ขึ้นต้นตรง) */
export async function commitMap(repo) {
  const r = await git(repo, ["log", "--reverse", "--format=%H%x09%s", "HEAD"]);
  const list = r.code === 0 ? r.out.split("\n").filter(Boolean).map((l) => { const [h, ...s] = l.split("\t"); return { h, s: s.join("\t") }; }) : [];
  const map = {};
  const order = [];
  for (const { h, s } of list) {
    const m = s.match(/^\s*EX\s*(\d)\s*(-\s*red)?\s*[:：]/i);
    if (!m) continue;
    const key = m[2] ? `EX${m[1]}-red` : `EX${m[1]}`;
    map[key] = h;
    order.push(key);
  }
  const head = (await git(repo, ["rev-parse", "HEAD"])).out.trim() || null;
  return { map, order, head, log: list };
}

// ───────────── แยกเคส ─────────────
/** ตัด block ของแต่ละเคสด้วยการนับวงเล็บ (ข้ามสตริง คอมเมนต์ และ regex literal) */
function blockEnd(text, start, limit) {
  let depth = 0, i = start, st = "code", q = "", prev = "(", cls = false;
  for (; i < limit; i++) {
    const c = text[i], n = text[i + 1];
    if (st === "code") {
      if (c === "/" && n === "/") { st = "lc"; i++; continue; }
      if (c === "/" && n === "*") { st = "bc"; i++; continue; }
      if (c === "/" && "(,=:[!&|?{};+-*%<>~^".includes(prev)) { st = "re"; cls = false; continue; }
      if (c === '"' || c === "'" || c === "`") { st = "str"; q = c; prev = c; continue; }
      if (c === "(") depth++;
      else if (c === ")") { depth--; if (depth === 0) return i + 1; }
      if (!/\s/.test(c)) prev = c;
    } else if (st === "lc") { if (c === "\n") st = "code"; }
    else if (st === "bc") { if (c === "*" && n === "/") { st = "code"; i++; } }
    else if (st === "str") { if (c === "\\") { i++; continue; } if (c === q) st = "code"; }
    else if (st === "re") {
      if (c === "\\") { i++; continue; }
      if (c === "[") cls = true; else if (c === "]") cls = false;
      else if (c === "/" && !cls) { st = "code"; prev = "a"; }
      else if (c === "\n") { st = "code"; }
    }
  }
  return limit;
}
const CASE_RE = {
  cr: /^[ \t]*T\(\s*["'`](E\d+)["'`]/gm,
  e2e: /^[ \t]*(?:tc|test)(?:\.\w+)?\(\s*["'`](TC-[A-Z]+-\d+)[^"'`]*["'`]/gm,
};
export function parseCases(text, kind) {
  const out = new Map();
  if (!text) return out;
  const files = Array.isArray(text) ? text : [text];
  for (const t of files) {
    const re = new RegExp(CASE_RE[kind].source, "gm");
    const hits = [...t.matchAll(re)];
    hits.forEach((m, k) => {
      const limit = k + 1 < hits.length ? hits[k + 1].index : t.length;
      const open = t.indexOf("(", m.index);
      const end = blockEnd(t, open, limit);
      out.set(m[1], (out.get(m[1]) ?? "") + t.slice(m.index, end));
    });
  }
  return out;
}
const norm = (s) => s.replace(/\/\/[^\n]*/g, "").replace(/\s+/g, " ").trim();
const ASSERT = { cr: /ck\.(eq|ok)\(/, e2e: /expect|toBe|toHave|toContain|toEqual|toMatch/ };
function literals(block, kind) {
  const lits = [];
  for (const line of block.split("\n")) {
    const l = line.replace(/\/\/.*$/, "");
    if (!ASSERT[kind].test(l)) continue;
    for (const m of l.matchAll(/(["'`])(?:\\.|(?!\1).)*\1|(?<![\w.])\d[\d_]*(?:\.\d+)?(?![\w])/g)) lits.push(m[0]);
  }
  return lits.sort().join("¦");
}
/** literal ทั้ง block (ไม่รวมคอมเมนต์) เป็น multiset */
function allLits(block) {
  const m = new Map();
  for (const x of block.replace(/\/\/[^\n]*/g, "").matchAll(/(["'`])(?:\\.|(?!\1).)*\1|(?<![\w.])\d[\d_]*(?:\.\d+)?(?![\w])/g)) m.set(x[0], (m.get(x[0]) ?? 0) + 1);
  return m;
}
/** literal เดิมหายไป/ถูกแทน (เพิ่มอย่างเดียว = เตรียมสถานการณ์) */
function litsRemoved(a, b) {
  const A = allLits(a), B = allLits(b);
  for (const [k, n] of A) if ((B.get(k) ?? 0) < n) return true;
  return false;
}
const SKIP_RE = /\b(test|tc|it|describe)\.(skip|fixme)\b|\bskip\s*:\s*true|info\.skip\(|test\.skip\(/;

/** เทียบเคสก่อน/หลัง → changed (ข้อความต่าง) · expectChanged (literal ในบรรทัดตรวจต่าง) · removed · added · failRemoved/failAdded · skipAdded */
export function diffCases(beforeText, afterText, kind) {
  const a = parseCases(beforeText, kind), b = parseCases(afterText, kind);
  const res = { changed: [], expectChanged: [], removed: [], added: [], failRemoved: [], failAdded: [], skipAdded: [] };
  for (const [id, blk] of a) {
    if (!b.has(id)) { res.removed.push(id); continue; }
    const nb = b.get(id);
    if (norm(blk) !== norm(nb)) res.changed.push(id);
    if (literals(blk, kind) !== literals(nb, kind) || litsRemoved(blk, nb)) res.expectChanged.push(id);
    const fa = /test\.fail\(/.test(blk.replace(/\/\/.*$/gm, "")), fb = /test\.fail\(/.test(nb.replace(/\/\/.*$/gm, ""));
    if (fa && !fb) res.failRemoved.push(id);
    if (!fa && fb) res.failAdded.push(id);
    if (!SKIP_RE.test(blk) && SKIP_RE.test(nb)) res.skipAdded.push(id);
  }
  for (const id of b.keys()) if (!a.has(id)) res.added.push(id);
  return res;
}

/** อ่าน check-rules + e2e-legacy/tests/*.ts ของ commit หนึ่ง */
export async function caseSources(repo, commit) {
  const cr = (await show(repo, commit, "web/scripts/check-rules.mjs")) ?? "";
  const e2e = [];
  for (const f of await lsFiles(repo, commit, "e2e-legacy/tests")) if (/\.ts$/.test(f)) e2e.push((await show(repo, commit, f)) ?? "");
  return { cr, e2e };
}
export async function caseDiff(repo, a, b) {
  if (!a || !b) return null;
  const A = await caseSources(repo, a), B = await caseSources(repo, b);
  const cr = diffCases(A.cr, B.cr, "cr"), e2e = diffCases(A.e2e, B.e2e, "e2e");
  const merged = {};
  for (const k of Object.keys(cr)) merged[k] = [...cr[k], ...e2e[k]];
  return merged;
}

// ───────────── ORACLE-CHANGES ─────────────
function expandIds(line) {
  const ids = new Set();
  for (const m of line.matchAll(/\bE(\d{2,3})\s*[–\-~]\s*E?(\d{2,3})\b/g)) for (let i = +m[1]; i <= +m[2] && i - +m[1] < 100; i++) ids.add(`E${String(i).padStart(2, "0")}`);
  for (const m of line.matchAll(/\bE\d{2,3}\b/g)) ids.add(m[0]);
  for (const m of line.matchAll(/\bTC-[A-Z]+-\d{2}\b/g)) ids.add(m[0]);
  return ids;
}
function itemsOf(line) {
  const s = new Set();
  for (const m of line.matchAll(/(?:ข้อ|item|Q|EX|#)\s*-?\s*([1-8])(?![0-9])/gi)) s.add(+m[1]);
  for (const m of line.matchAll(/\|\s*([4-8])\s*(?=\|)/g)) s.add(+m[1]);
  return s;
}
export function parseOracle(text) {
  if (!text) return [];
  return text.split("\n").filter((l) => l.trim()).map((line) => ({ line, ids: expandIds(line), items: itemsOf(line) }));
}
/** มีแถวที่อ้าง id (หรือชื่อไฟล์ golden) และอ้างข้อในรายการ items */
export function oracleHas(rows, id, items) {
  const want = Array.isArray(items) ? items : [items];
  return rows.some((r) => (r.ids.has(id) || (!/^E\d|^TC-/.test(id) && r.line.includes(id))) && want.some((n) => r.items.has(n)));
}

// ───────────── ข้อ 1 / ข้อ 3 ─────────────
const rx = (p) => new RegExp(p, "i");
export function gradeQ1(json, key) {
  const rows = [];
  let total = 0;
  for (const [q, spec] of Object.entries(key)) {
    const a = json?.[q];
    let got = 0;
    const notes = [];
    if (!a) { rows.push({ q, score: 0, note: "ไม่มีคำตอบ" }); continue; }
    const files = [a.file].flat().filter(Boolean).map((f) => String(f).replace(/\\/g, "/").replace(/^\.?\//, ""));
    const text = JSON.stringify(a);
    for (const p of spec.parts) {
      const fileOk = files.some((f) => p.file.some((pf) => rx(`(^|/)${pf}$`).test(f) || rx(pf).test(f)));
      const allOk = (p.all ?? []).every((r) => rx(r).test(text));
      const anyN = (p.any ?? []).filter((r) => rx(r).test(text)).length;
      const anyOk = !p.any || anyN >= (p.min ?? 1);
      if (fileOk && allOk && anyOk) got += p.w;
      else notes.push(`${fileOk ? "" : "ไฟล์ไม่ตรง "}${allOk ? "" : "คำตอบ/ชื่อไม่ตรง "}${anyOk ? "" : `พบ ${anyN}/${p.min ?? 1} ประเด็น`}`.trim() + (fileOk ? " (path ถูก → ผู้สอนพิจารณาครึ่ง)" : ""));
    }
    got = Math.round(got * 100) / 100;
    total += got;
    rows.push({ q, score: got, note: notes.join(" · ") });
  }
  return { score: Math.round(total * 100) / 100, rows };
}
export function gradeImpact(text, key) {
  const found = [], missing = [];
  for (const p of key) (p.re.some((r) => rx(r).test(text ?? "")) ? found : missing).push(p);
  const score = Math.floor((6 * found.length) / key.length * 2) / 2;
  return { score, found: found.map((p) => p.id), missing: missing.map((p) => `${p.id} ${p.label}`) };
}

// ───────────── REGRESSION.md ─────────────
/** หา "ตัวเลข" ที่ผู้สอบเขียน: คืน true ถ้าตัวเลขของเครื่องตรวจปรากฏในบริบทที่ถูก */
export function regressionMatches(text, g) {
  const t = (text ?? "").replace(/,/g, "");
  const has = (re) => re.test(t);
  const res = {};
  if (g.e2e) {
    res.passed = has(new RegExp(`(^|\\D)${g.e2e.passed}\\s*(passed|ผ่าน)|(passed|ผ่าน)\\s*[:=]?\\s*${g.e2e.passed}(\\D|$)`, "i"));
    res.failed = has(new RegExp(`(^|\\D)${g.e2e.failed}\\s*(failed|ล้ม|ไม่ผ่าน)|(?<!expected[- ]?)(failed|ล้ม|ไม่ผ่าน)\\s*[:=]?\\s*${g.e2e.failed}(\\D|$)`, "i"));
    res.expectedFail = has(new RegExp(`(^|\\D)${g.e2e.expectedFail}\\s*(expected[- ]?fail|คาดว่าล้ม)|(expected[- ]?fail\\w*|คาดว่าล้ม)\\s*\\W{0,3}\\s*${g.e2e.expectedFail}(\\D|$)`, "i"));
  }
  if (g.checkRules) res.checkRules = has(new RegExp(`(^|\\D)${g.checkRules.passed}\\s*/\\s*${g.checkRules.total}(\\D|$)`));
  if (g.golden) res.golden = has(new RegExp(`(^|\\D)${g.golden.passed}\\s*/\\s*${g.golden.total}(\\D|$)`));
  return res;
}
