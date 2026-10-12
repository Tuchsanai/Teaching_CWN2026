#!/usr/bin/env node
// เครื่องตรวจอัตโนมัติ ข้อสอบบท 06 (ชุด A / B) · เรียกผ่าน grade.ps1 · Node ≥ 22 บนเครื่องผู้สอน + Docker Desktop
//   node grade.mjs --submission <โฟลเดอร์|.bundle> --set A|B --variant 0..2 [--id ชื่อ] [--work dir] [--out dir]
//                  [--prefix exref-g] [--e2e full|quick|skip] [--keep] [--map EX4=<sha>,...]
//   node grade.mjs --prep --set A|B        เตรียม image ฐาน + mutant + node_modules ของ Playwright ครั้งเดียว
//   node grade.mjs --cleanup [--images]    ลบ container/network (และ image) ที่ขึ้นต้นด้วย prefix
import { parseArgs } from "node:util";
import { fileURLToPath } from "node:url";
import { dirname, resolve, join, basename } from "node:path";
import { homedir } from "node:os";
import { existsSync, mkdirSync, rmSync, cpSync, readFileSync, writeFileSync, readdirSync, appendFileSync, statSync } from "node:fs";
import { sh } from "./lib/sh.mjs";
import { IMG, Sut, ensureImage, ensureNetwork, pwSummary, cleanupPrefix } from "./lib/docker.mjs";
import * as S from "./lib/static.mjs";
import { rubric, ITEM_MAX } from "./lib/rubric.mjs";

const GRADER = dirname(fileURLToPath(import.meta.url));
const { values: o } = parseArgs({
  options: {
    submission: { type: "string" }, set: { type: "string" }, variant: { type: "string" }, id: { type: "string" },
    work: { type: "string" }, out: { type: "string" }, prefix: { type: "string" }, e2e: { type: "string" },
    keep: { type: "boolean" }, prep: { type: "boolean" }, cleanup: { type: "boolean" }, images: { type: "boolean" },
    base: { type: "string" }, map: { type: "string" },
  },
});
const PREFIX = (o.prefix ?? "exref-g").toLowerCase();
const WORK = resolve(o.work ?? join(homedir(), "sabai-grader-work"));
const CHAPTER = resolve(o.base ?? join(GRADER, "..", ".."));
const EXREF = join(GRADER, "..", "exam-ref");
const E2E_MODE = o.e2e ?? "full";
const T0 = Date.now();
const sec = (ms) => Math.round(ms / 1000);
const fwd = (p) => p.replace(/\\/g, "/");

if (o.cleanup) {
  const r = await cleanupPrefix(PREFIX, { images: !!o.images });
  console.log(`cleanup ${PREFIX}: ${JSON.stringify(r)}`);
  process.exit(0);
}
const SET = (o.set ?? "").toUpperCase();
if (!["A", "B"].includes(SET)) { console.error("ต้องระบุ --set A หรือ B"); process.exit(2); }
const KEY = JSON.parse(readFileSync(join(GRADER, "keys", `${SET}.json`), "utf8"));
const VARIANTS = JSON.parse(readFileSync(join(GRADER, "variants.json"), "utf8"));
const SHARED = join(WORK, "_shared");
mkdirSync(SHARED, { recursive: true });

// ───────────── เตรียมครั้งเดียว ─────────────
const COPY_FILTER = (src) => !/[\\/](node_modules|\.next|test-report|out)([\\/]|$)/.test(src.slice(CHAPTER.length));
async function prepShared(log) {
  const t = Date.now();
  const base = join(SHARED, "base");
  if (!existsSync(join(base, ".git"))) {
    rmSync(base, { recursive: true, force: true });
    mkdirSync(base, { recursive: true });
    for (const d of ["web", "db", "e2e-legacy"]) cpSync(join(CHAPTER, d), join(base, d), { recursive: true, filter: COPY_FILTER });
    await S.git(base, ["init", "-q"]);
    await S.git(base, ["add", "-A"]);
    await S.git(base, ["-c", "user.name=grader", "-c", "user.email=grader@local", "commit", "-qm", "EX0: base (grader)"]);
  }
  const baseTag = await tagFor(base, "HEAD");
  const jobs = [ensureImage(baseTag, join(base, "web"), join(base, "db", "init"), log)];
  const mutTags = {};
  for (const m of KEY.mutants) {
    const d = join(SHARED, "mut", m);
    if (!existsSync(join(d, ".git"))) {
      rmSync(d, { recursive: true, force: true });
      cpSync(base, d, { recursive: true });
      const r = await S.git(d, ["apply", fwd(join(EXREF, "mutants", `${m}.diff`))]);
      if (r.code !== 0) throw new Error(`git apply ${m}: ${r.err}`);
      await S.git(d, ["-c", "user.name=grader", "-c", "user.email=grader@local", "commit", "-qam", `mutant ${m}`]);
    }
    mutTags[m] = await tagFor(d, "HEAD");
    jobs.push(ensureImage(mutTags[m], join(d, "web"), join(d, "db", "init"), log));
  }
  // node_modules ของ Playwright (จาก package-lock ของ e2e-legacy ตั้งต้น)
  const nm = join(SHARED, "e2e-nm");
  if (!existsSync(join(nm, "node_modules", "@playwright", "test"))) {
    mkdirSync(nm, { recursive: true });
    for (const f of ["package.json", "package-lock.json"]) cpSync(join(base, "e2e-legacy", f), join(nm, f));
    log("npm ci (Playwright 1.63) …");
    jobs.push(sh("docker", ["run", "--rm", "--label", `sabai-grader=${PREFIX}`, "-v", `${fwd(nm)}:/e`, "-w", "/e", IMG.pw, "npm", "ci", "--no-audit", "--no-fund"], { timeoutMs: 15 * 60_000 })
      .then((r) => { if (r.code !== 0) throw new Error("npm ci: " + r.err.slice(-500)); return { ok: true }; }));
  }
  const res = await Promise.all(jobs);
  const bad = res.filter((x) => x && x.ok === false);
  if (bad.length) throw new Error("build image ฐาน/mutant ไม่สำเร็จ: " + bad.map((b) => b.err).join("\n"));
  log(`เตรียมครั้งเดียวเสร็จ (${sec(Date.now() - t)} วินาที)`);
  return { base, baseTag, mutTags, nm: join(nm, "node_modules"), ms: Date.now() - t };
}
async function tagFor(repo, commit) {
  const w = await S.treeHash(repo, commit, "web");
  const i = await S.treeHash(repo, commit, "db/init");
  if (!w || !i) return null;
  return `${PREFIX}-web:${w.slice(0, 10)}-${i.slice(0, 10)}`;
}

if (o.prep) {
  const p = await prepShared((m) => console.log(`[prep] ${m}`));
  console.log(JSON.stringify({ baseTag: p.baseTag, mutTags: p.mutTags, seconds: sec(p.ms) }));
  process.exit(0);
}

// ───────────── ต่อผู้สอบ 1 คน ─────────────
if (!o.submission) { console.error("ต้องระบุ --submission"); process.exit(2); }
const SUB = resolve(o.submission);
const ID = (o.id ?? basename(SUB).replace(/\.bundle$/i, "")).toLowerCase().replace(/[^a-z0-9-]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 30) || "sub";
const W = join(WORK, ID);
const OUT = resolve(o.out ?? join(WORK, "results", ID));
rmSync(W, { recursive: true, force: true });
mkdirSync(W, { recursive: true });
mkdirSync(OUT, { recursive: true });
const LOG = join(OUT, "grade.log");
writeFileSync(LOG, "");
const log = (m) => { const l = `[${String(sec(Date.now() - T0)).padStart(4)}s] ${m}`; console.log(l); appendFileSync(LOG, l + "\n"); };

let variantNo = o.variant !== undefined ? Number(o.variant) : null;
const ctx = { prefix: PREFIX, id: ID, net: `${PREFIX}-${ID}-net`, log };
const R = rubric(SET);
const row = (item, key) => R.find((r) => r.item === item && r.key === key);
const setRow = (item, key, score, detail) => { const r = row(item, key); if (!r) return; if (score !== undefined && score !== null) r.score = Math.round(Math.min(score, r.max) * 100) / 100; if (detail) r.detail = detail; };
const notes = []; // หมายเหตุทั่วไป
const penalties = []; // {item, factor, why}
const timings = {};
const raw = {}; // ผลดิบเก็บลง raw.json

async function timed(name, fn) { const t = Date.now(); try { return await fn(); } finally { timings[name] = sec(Date.now() - t); } }

// 1) ได้ repo ของผู้สอบ (ไม่แตะโฟลเดอร์ต้นฉบับ)
const REPO = join(W, "repo");
await timed("clone", async () => {
  if (/\.bundle$/i.test(SUB)) {
    const r = await sh("git", ["clone", "-q", fwd(SUB), fwd(REPO)]);
    if (r.code !== 0) throw new Error("git clone bundle: " + r.err);
  } else if (existsSync(join(SUB, ".git"))) {
    const r = await sh("git", ["clone", "-q", "--no-hardlinks", fwd(SUB), fwd(REPO)]);
    if (r.code !== 0) throw new Error("git clone: " + r.err);
  } else {
    notes.push("โฟลเดอร์ที่ส่งไม่มี .git → เครื่องตรวจสร้าง commit เดียว (EX0) จากไฟล์ที่มี · ไม่มี commit ของข้อใดเลย");
    cpSync(SUB, REPO, { recursive: true, filter: (s) => !/[\\/](node_modules|\.next|test-report)([\\/]|$)/.test(s.slice(SUB.length)) });
    await S.git(REPO, ["init", "-q"]);
    await S.git(REPO, ["add", "-A"]);
    await S.git(REPO, ["-c", "user.name=grader", "-c", "user.email=grader@local", "commit", "-qm", "EX0: base (สร้างโดยเครื่องตรวจ)"]);
  }
  await S.git(REPO, ["config", "core.autocrlf", "false"]);
});
const CM = await S.commitMap(REPO);
const C = { ...CM.map };
if (o.map) for (const kv of o.map.split(",")) { const [k, v] = kv.split("="); if (k && v) C[k.trim()] = (await S.git(REPO, ["rev-parse", v.trim()])).out.trim(); }
if (!C.EX0) { C.EX0 = CM.log[0]?.h; notes.push("ไม่พบ commit EX0 → ใช้ commit แรกของ repo"); }
const HEAD = CM.head;
raw.commits = C;
log(`commit: ${Object.entries(C).map(([k, v]) => `${k}=${v?.slice(0, 7)}`).join(" ")} · HEAD=${HEAD?.slice(0, 7)}`);
const SEQ = ["EX0", "EX1", "EX2", "EX3", "EX4", "EX5-red", "EX5", "EX6", "EX7", "EX8"];
const missing = SEQ.filter((k) => !C[k]);
if (missing.length) notes.push(`ไม่พบ commit: ${missing.join(" ")}`);
const orderOk = SEQ.filter((k) => C[k]).every((k, i, arr) => i === 0 || CM.log.findIndex((x) => x.h === C[arr[i - 1]]) < CM.log.findIndex((x) => x.h === C[k]));
if (!orderOk) notes.push("⚠️ ลำดับ commit EX* ไม่ตรงลำดับข้อ");

// VARIANT
let VAR = null;
const subVar = await S.show(REPO, HEAD, "exam/VARIANT.json");
if (variantNo === null && subVar) { try { variantNo = Number(JSON.parse(subVar).v); } catch { /* ignore */ } }
VAR = VARIANTS[SET][variantNo ?? 0];
if (!VAR) { console.error(`ไม่มี variant ${variantNo} ของชุด ${SET}`); process.exit(2); }
if (subVar) { try { const sv = JSON.parse(subVar); if (sv.set !== SET || Number(sv.v) !== VAR.v) notes.push(`⚠️ exam/VARIANT.json ของผู้สอบ (${sv.set} v${sv.v}) ≠ ที่สั่งตรวจ (${SET} v${VAR.v})`); } catch { notes.push("⚠️ exam/VARIANT.json อ่านไม่ได้"); } }
log(`ตรวจชุด ${SET} variant ${VAR.v} · ${JSON.stringify(VAR)}`);

const prevOf = (k) => { const i = SEQ.indexOf(k); for (let j = i - 1; j >= 0; j--) if (C[SEQ[j]]) return C[SEQ[j]]; return C.EX0; };
const diffNonEmpty = async (a, b) => a && b && (await S.git(REPO, ["diff", "--quiet", a, b])).code === 1;
const itemCommit = (n) => (n === 5 ? C.EX5 ?? C["EX5-red"] : C[`EX${n}`]);
const itemFrom = (n) => (n === 5 ? prevOf(C["EX5-red"] ? "EX5-red" : "EX5") : prevOf(`EX${n}`));
const DONE = {};
for (let n = 1; n <= 8; n++) DONE[n] = !!itemCommit(n) && (await diffNonEmpty(itemFrom(n), itemCommit(n)));
log(`ข้อที่มีงาน: ${Object.entries(DONE).filter(([, v]) => v).map(([k]) => k).join(",") || "-"}`);
const notDone = (n) => `ไม่มีงานข้อ ${n} (${itemCommit(n) ? "commit ว่าง/skip" : "ไม่พบ commit"})`;

// worktree ของแต่ละ commit (ใช้ build/รันสคริปต์ของผู้สอบ)
const trees = {};
async function tree(k) {
  const h = k === "HEAD" ? HEAD : C[k];
  if (!h) return null;
  if (trees[h]) return trees[h];
  const d = join(W, "trees", h.slice(0, 10));
  trees[h] = (async () => {
    const r = await S.git(REPO, ["worktree", "add", "-f", "--detach", fwd(d), h]);
    if (r.code !== 0) throw new Error("worktree: " + r.err);
    return d;
  })();
  return trees[h];
}

// ───────────── ตรวจแบบไม่ต้องเปิดระบบ ─────────────
const ORA_HEAD = S.parseOracle(await S.show(REPO, HEAD, "exam/ORACLE-CHANGES.md"));
await timed("static", async () => {
  // ไฟล์ที่ต้องส่ง
  raw.files = [];
  for (const f of KEY.files) {
    const at = C[f.commit] ?? HEAD;
    const ok = f.dir ? (await S.lsFiles(REPO, at, f.path)).length > 0 : (await S.show(REPO, at, f.path)) !== null;
    const okHead = f.dir ? (await S.lsFiles(REPO, HEAD, f.path)).length > 0 : (await S.show(REPO, HEAD, f.path)) !== null;
    raw.files.push({ ...f, atCommit: C[f.commit] ? ok : null, atHead: okHead });
  }
  // ข้อ 1
  if (DONE[1]) {
    const txt = await S.show(REPO, C.EX1, "exam/Q1.json");
    let js = null;
    try { js = JSON.parse(txt ?? ""); } catch { /* ignore */ }
    if (!js) setRow(1, "q1", 0, "ไม่มี/อ่าน exam/Q1.json ไม่ได้ (JSON)");
    else {
      const g = S.gradeQ1(js, KEY.ex1);
      raw.q1 = g;
      setRow(1, "q1", g.score, g.rows.filter((r) => r.score < (KEY.ex1[r.q].parts.reduce((a, p) => a + p.w, 0))).map((r) => `${r.q}=${r.score} (${r.note})`).join(" · ") || "ถูกทุกข้อ");
    }
  } else setRow(1, "q1", 0, notDone(1));
  // ข้อ 3
  if (DONE[3]) {
    const txt = await S.show(REPO, C.EX3, "exam/IMPACT.md");
    const g = S.gradeImpact(txt ?? "", KEY.ex3);
    raw.impact = g;
    setRow(3, "impact", txt ? g.score : 0, txt ? `พบ ${g.found.length}/${KEY.ex3.length}${g.missing.length ? " · ไม่พบ: " + g.missing.join(" | ") : ""}` : "ไม่มี exam/IMPACT.md");
    const ch = await S.changedFiles(REPO, prevOf("EX3"), C.EX3);
    const outside = ch.filter((f) => !f.startsWith("exam/"));
    row(3, "proof").detail = outside.length ? `⚠️ commit EX3 แก้ไฟล์นอก exam/: ${outside.join(", ")} (ผู้สอนหัก 1)` : "EX3 แตะเฉพาะ exam/";
  } else setRow(3, "impact", 0, notDone(3));

  // เคสเดิมที่เปลี่ยนในแต่ละข้อ + กติกาหักคะแนน
  raw.caseDiffs = {};
  for (const n of [2, 3, 4, 5, 6, 7, 8]) {
    if (!DONE[n]) continue;
    const d = await S.caseDiff(REPO, itemFrom(n), itemCommit(n));
    raw.caseDiffs[n] = d;
    if (d.removed.length || d.skipAdded.length) penalties.push({ item: n, factor: 0, why: `ลบ/skip เทสต์เดิม: ${[...d.removed, ...d.skipAdded].join(" ")}` });
    const noRow = d.expectChanged.filter((id) => !S.oracleHas(ORA_HEAD, id, [4, 5, 6, 7, 8]));
    if (noRow.length) penalties.push({ item: n, factor: 0.5, why: `เปลี่ยนค่าคาดหวังโดยไม่มีแถว ORACLE: ${noRow.join(" ")}` });
    if (C.EX2 && n > 2) {
      const gch = (await S.changedFiles(REPO, itemFrom(n), itemCommit(n), ["tests/exam2/golden"])).map((f) => basename(f).replace(/\.json$/, ""));
      const gNo = gch.filter((g) => !S.oracleHas(ORA_HEAD, g, [4, 5, 6, 7, 8]));
      if (gNo.length) penalties.push({ item: n, factor: 0.5, why: `แก้ golden ข้อ 2 โดยไม่มีแถว ORACLE: ${gNo.join(" ")}` });
    }
  }
  // down -v ในขั้นตอนที่ส่ง
  const DV = /down\s+(-v\b|--volumes\b)/;
  const mig = await S.lsFiles(REPO, HEAD, "db/migrations");
  for (const f of ["exam/MIGRATION.md", ...mig]) if (DV.test((await S.show(REPO, HEAD, f)) ?? "")) penalties.push({ item: 6, factor: 0, why: `พบ "down -v" ใน ${f}` });
  if (DV.test((await S.show(REPO, HEAD, "RELEASE-NOTES.md")) ?? "")) penalties.push({ item: 8, factor: 0, why: `พบ "down -v" ใน RELEASE-NOTES.md` });

  // ข้อ 4: เคสที่แก้ + ORACLE
  if (DONE[4]) {
    const d = raw.caseDiffs[4];
    const must = KEY.ex4.mustChange;
    const got = [...new Set(d.expectChanged)];
    const lack = must.filter((x) => !got.includes(x)), extra = got.filter((x) => !must.includes(x));
    setRow(4, "cases", lack.length || extra.length ? 0 : 1, `เปลี่ยนค่าคาดหวัง: ${got.join(" ") || "-"}${lack.length ? ` · ขาด ${lack.join(" ")}` : ""}${extra.length ? ` · เกิน ${extra.join(" ")}` : ""}`);
    const ora4 = S.parseOracle(await S.show(REPO, C.EX4, "exam/ORACLE-CHANGES.md"));
    const noRow = got.filter((id) => !S.oracleHas(ora4, id, 4));
    setRow(4, "oracle", got.length && !noRow.length ? 1 : 0, got.length ? (noRow.length ? `ไม่มีแถวอ้างข้อ 4 (ไฟล์ที่ EX4): ${noRow.join(" ")}` : `ครบ ${got.length} เคส`) : "ไม่มีเคสที่เปลี่ยน");
  } else for (const k of ["cases", "oracle"]) setRow(4, k, 0, notDone(4));

  // ข้อ 5: เทสต์เดิม
  if (DONE[5]) {
    const d = raw.caseDiffs[5];
    const ora = S.parseOracle(await S.show(REPO, C.EX5 ?? HEAD, "exam/ORACLE-CHANGES.md"));
    if (SET === "A") {
      const need = KEY.ex5.statusChange;
      const ok = need.every((id) => d.failRemoved.includes(id) && S.oracleHas(ora, id, 5));
      const extra = d.expectChanged.filter((x) => !need.includes(x));
      setRow(5, "legacy", ok && !extra.length ? 1 : 0, `เอา test.fail ออก: ${d.failRemoved.join(" ") || "-"} · ORACLE ข้อ 5: ${need.map((id) => `${id}=${S.oracleHas(ora, id, 5) ? "มี" : "ไม่มี"}`).join(" ")}${extra.length ? ` · เปลี่ยนค่าคาดหวังเคสอื่น: ${extra.join(" ")}` : ""}`);
    } else {
      const need = KEY.ex5.setupOnly;
      const changed = [...new Set(d.changed)];
      const lack = need.filter((x) => !changed.includes(x)), extra = changed.filter((x) => !need.includes(x));
      const exp = d.expectChanged;
      const noRow = changed.filter((id) => !S.oracleHas(ora, id, 5));
      setRow(5, "legacy", !lack.length && !extra.length && !exp.length && !noRow.length ? 1 : 0,
        `แก้: ${changed.join(" ") || "-"}${lack.length ? ` · ขาด ${lack.join(" ")}` : ""}${extra.length ? ` · เกิน ${extra.join(" ")}` : ""}${exp.length ? ` · เปลี่ยนตัวเลขคาดหวัง ${exp.join(" ")}` : ""}${noRow.length ? ` · ไม่มีแถว ORACLE ข้อ 5: ${noRow.join(" ")}` : ""}`);
    }
  } else setRow(5, "legacy", 0, notDone(5));

  // ข้อ 8 ②
  if (DONE[8]) {
    const d = await S.caseDiff(REPO, C.EX0, HEAD);
    const gold = C.EX2 ? (await S.changedFiles(REPO, C.EX2, HEAD, ["tests/exam2/golden"])).map((f) => basename(f).replace(/\.json$/, "")) : [];
    const all = [...new Set([...d.expectChanged, ...d.failRemoved, ...gold])];
    const cov = all.filter((id) => S.oracleHas(ORA_HEAD, id, [4, 5, 6, 7]));
    const miss = all.filter((id) => !cov.includes(id));
    setRow(8, "oracle", all.length ? Math.floor((2 * cov.length) / all.length * 2) / 2 : 0, all.length ? `มีแถว ${cov.length}/${all.length}${miss.length ? " · ขาด: " + miss.join(" ") : ""}` : "ไม่มีเคสที่เปลี่ยน/ไม่มี ORACLE");
  } else setRow(8, "oracle", 0, notDone(8));
});
log(`ตรวจแบบ static เสร็จ`);

// ───────────── เตรียม image / ระบบ ─────────────
const P = await timed("prep-shared", () => prepShared(log));
await ensureNetwork(ctx.net);
const HIDDEN = join(GRADER, "hidden");
const isTest = (f) => !f.startsWith("exam/") && /\.(mjs|js|cjs|ts)$/.test(f) && !/golden\//.test(f) && !/(^|\/)(fixtures|global-setup|playwright\.config)\b/.test(f) && f !== "tests/smoke.mjs" &&
  (/(^|\/)tests?\//.test(f) || /\.(spec|test)\.(ts|mjs|js)$/.test(f) || f === "web/scripts/check-rules.mjs");

const need = {
  main: [4, 5, 6, 7, 8].some((n) => DONE[n]),
  e2e: DONE[8] && E2E_MODE !== "skip" && (await S.show(REPO, HEAD, "exam/REGRESSION.md")) !== null,
  fresh: DONE[6],
};
const tagHEAD = need.main || need.e2e ? await tagFor(REPO, HEAD) : null;
const commitTags = {};
for (const k of ["EX4", "EX5-red", "EX5", "EX7"]) if (C[k]) commitTags[k] = await tagFor(REPO, C[k]);

// งานที่ต้องรันบน image ของ commit ใด ๆ (จัดกลุ่มตาม tag)
const groups = new Map(); // tag → { initFrom: key, tasks: [] }
const addTask = (key, task) => {
  const tag = commitTags[key];
  if (!tag) return;
  if (!groups.has(tag)) groups.set(tag, { initFrom: key, tasks: [] });
  groups.get(tag).tasks.push(task);
};

// check-rules ต่อข้อ
const crRes = {};
async function runCheckRules(sut, treeDir, label) {
  if (!existsSync(join(treeDir, "web", "scripts", "check-rules.mjs"))) return { code: 2, passed: 0, total: 0, failed: "ไม่มีไฟล์" };
  const r = await sut.node("web/scripts/check-rules.mjs", { mounts: [[treeDir, "/w"]], tag: "cr", timeoutMs: 10 * 60_000 });
  const m = r.out.match(/ผ่าน\s+(\d+)\s*\/\s*(\d+)/);
  const f = r.out.match(/รายการที่ล้ม:\s*(.*)/);
  log(`check-rules ${label} → exit ${r.code} ${m ? `${m[1]}/${m[2]}` : ""} ${f ? "ล้ม " + f[1] : ""}`);
  return { code: r.code, passed: m ? +m[1] : 0, total: m ? +m[2] : 0, failed: f ? f[1].trim() : r.code ? (r.err || r.out).slice(-300) : "" };
}
for (const [k, n] of [["EX4", 4], ["EX5", 5], ["EX7", 7]]) {
  if (!DONE[n] || !C[k]) { setRow(n, "cr", 0, notDone(n)); continue; }
  addTask(k, async (sut) => { crRes[n] = await runCheckRules(sut, await tree(k), k); });
}

// เทสต์ของผู้สอบ (ข้อ 5 แดง/เขียว · ข้อ 7)
async function runLearnerTests(sut, treeDir, files, label) {
  const res = [];
  for (const f of files) {
    if (!existsSync(join(treeDir, f))) { res.push({ file: f, code: 404, note: "ไม่มีไฟล์ใน commit นี้" }); continue; }
    let r;
    if (/\.spec\.ts$|\.test\.ts$/.test(f)) {
      const runDir = join(W, "pw-" + label + "-" + basename(treeDir));
      if (!existsSync(runDir)) cpSync(join(treeDir, "e2e-legacy"), runDir, { recursive: true, filter: (s) => !/[\\/](node_modules|test-report|out)([\\/]|$)/.test(s.slice(treeDir.length)) });
      let rel;
      if (f.startsWith("e2e-legacy/")) rel = f.slice("e2e-legacy/".length);
      else { mkdirSync(join(runDir, "tests", "zz-learner"), { recursive: true }); cpSync(join(treeDir, f), join(runDir, "tests", "zz-learner", basename(f))); rel = `tests/zz-learner/${basename(f)}`; }
      const project = /\.api\.spec\.ts$/.test(f) ? "api" : "chromium";
      r = await sut.playwright(runDir, P.nm, [rel, `--project=${project}`, "--reporter=list"], { tag: "lt", timeoutMs: 15 * 60_000 });
    } else if (f === "web/scripts/check-rules.mjs") {
      r = await sut.node(f, { mounts: [[treeDir, "/w"]], tag: "lt" });
    } else {
      r = await sut.node(f, { mounts: [[treeDir, "/w"]], tag: "lt", timeoutMs: 10 * 60_000 });
    }
    res.push({ file: f, code: r.code, tail: (r.out + r.err).trim().split("\n").slice(-4).join(" ⏎ ").slice(0, 400) });
    log(`เทสต์ผู้สอบ ${label} ${f} → exit ${r.code}`);
  }
  return res;
}
let redFiles = [], redRes = null, greenRes = null;
if (DONE[5] && C["EX5-red"]) {
  redFiles = (await S.changedFiles(REPO, prevOf("EX5-red"), C["EX5-red"])).filter(isTest);
  if (redFiles.length && C.EX5) {
    addTask("EX5-red", async (sut) => { redRes = await runLearnerTests(sut, await tree("EX5-red"), redFiles, "red"); });
    addTask("EX5", async (sut) => { greenRes = await runLearnerTests(sut, await tree("EX5"), redFiles, "green"); });
  }
}
let ownFiles = [], ownRes = null;
if (DONE[7]) ownFiles = (await S.changedFiles(REPO, prevOf("EX7"), C.EX7)).filter(isTest).filter((f) => f !== "web/scripts/check-rules.mjs" || true);


// ───────────── lanes (ขนาน) ─────────────
const parseResult = (out) => { const l = out.split("\n").reverse().find((x) => x.startsWith("RESULT ")); try { return l ? JSON.parse(l.slice(7)) : null; } catch { return null; } };
const hiddenEnv = { VARIANT_JSON: JSON.stringify(VAR) };
async function hidden(sut, file, extra = {}) {
  const head = await tree("HEAD");
  const r = await sut.node(`/h/${SET}/${file}`, { mounts: [[HIDDEN, "/h", true], [head, "/l", true], ...(extra.mounts ?? [])], env: { ...hiddenEnv, LEARNER: "/l", ...(extra.env ?? {}) }, tag: "h", cwd: "/h", timeoutMs: 10 * 60_000 });
  const res = parseResult(r.out);
  appendFileSync(join(OUT, "hidden.log"), `\n===== ${file} (exit ${r.code})\n${r.out}\n${r.err.slice(-2000)}\n`);
  if (!res) log(`hidden ${file}: ไม่ได้ผล (exit ${r.code}) ${r.err.slice(-300)}`);
  else log(`hidden ${file}: ${res.score}/${res.max}`);
  return res;
}
const H = {}; // ผล hidden
const sumChecks = (checks, pred) => checks.filter(pred).reduce((a, c) => a + (c.ok ? c.weight : 0), 0);
const failList = (checks, pred) => checks.filter((c) => pred(c) && !c.ok).map((c) => `${c.id}: ${c.detail}`).join(" | ");

async function laneBase() {
  const ex2Tree = C.EX2 && DONE[2] ? await tree("EX2") : null;
  const hasGolden = ex2Tree && existsSync(join(ex2Tree, "tests", "exam2", "run.mjs"));
  const smokeHead = DONE[8] && (await S.show(REPO, HEAD, "tests/smoke.mjs")) !== null;
  const evid = SET === "B" && DONE[5] ? ((C["EX5-red"] && (await S.show(REPO, C["EX5-red"], "exam/EX5-EVIDENCE.json"))) ?? (await S.show(REPO, HEAD, "exam/EX5-EVIDENCE.json"))) : null;
  if (!hasGolden && !smokeHead && !evid) {
    for (const r of R.filter((x) => x.item === 2 && x.kind === "auto")) setRow(2, r.key, 0, DONE[2] ? "ไม่มี tests/exam2/run.mjs ใน EX2" : notDone(2));
    return;
  }
  const base = new Sut(ctx, "base");
  const muts = hasGolden ? KEY.mutants.map((m) => ({ m, sut: new Sut(ctx, m.toLowerCase()) })) : [];
  const runGolden = (sut) => sut.node("tests/exam2/run.mjs", { mounts: [[ex2Tree, "/w"]], tag: "g2", timeoutMs: 8 * 60_000 });
  const tasks = [];
  tasks.push((async () => {
    await base.start(P.baseTag, join(P.base, "db", "init"));
    if (hasGolden) {
      const r = await runGolden(base);
      raw.goldenBase = { code: r.code, tail: r.out.split("\n").slice(-5).join(" ⏎ ") };
      log(`golden EX2 บนระบบตั้งต้น → exit ${r.code}`);
      setRow(2, "gate", 0, r.code === 0 ? "ผ่าน (exit 0)" : `❌ exit ${r.code} → ข้อ 2 ได้ 0 · ${raw.goldenBase.tail.slice(-300)}`);
    }
    if (smokeHead) {
      const r = await base.node("tests/smoke.mjs", { mounts: [[await tree("HEAD"), "/w"]], tag: "sm", timeoutMs: 5 * 60_000 });
      raw.smokeBase = { code: r.code, tail: (r.out + r.err).split("\n").slice(-4).join(" ⏎ ").slice(0, 400) };
      log(`smoke บนระบบตั้งต้น → exit ${r.code} (ต้อง ≠ 0)`);
    }
    if (evid) {
      const ev = join(W, "evidence");
      mkdirSync(ev, { recursive: true });
      writeFileSync(join(ev, "EX5-EVIDENCE.json"), evid);
      H.evidence = await hidden(base, "ex5-evidence.mjs", { mounts: [[ev, "/x", true]], env: { EVIDENCE: "/x/EX5-EVIDENCE.json" } });
    }
    await base.stop();
  })());
  for (const { m, sut } of muts) {
    tasks.push((async () => {
      try {
        await sut.start(P.mutTags[m], join(P.base, "db", "init"));
        const r = await runGolden(sut);
        raw[`golden_${m}`] = { code: r.code, tail: r.out.split("\n").filter((l) => /DIFF|FAIL|ต่าง|match|ผ่าน/i.test(l)).slice(0, 3).join(" ⏎ ").slice(0, 300) };
        log(`golden EX2 บน ${m} → exit ${r.code}`);
      } catch (e) { raw[`golden_${m}`] = { code: null, tail: String(e.message ?? e).slice(0, 300) }; }
      await sut.stop();
    })());
  }
  await Promise.all(tasks);
  if (hasGolden) {
    const gate = raw.goldenBase?.code === 0;
    for (const m of KEY.mutants) {
      const g = raw[`golden_${m}`];
      const killed = g && g.code !== null && g.code !== 0;
      setRow(2, m.toLowerCase(), gate && killed ? 3 : 0, !gate ? "ระบบตั้งต้นไม่ผ่าน → 0" : killed ? `จับได้ (exit ${g.code}) ${g.tail}` : `จับไม่ได้ (exit ${g?.code}) ${g?.tail ?? ""}`);
    }
  } else for (const r of R.filter((x) => x.item === 2 && x.kind === "auto")) setRow(2, r.key, 0, DONE[2] ? "ไม่มี tests/exam2/run.mjs ใน EX2" : notDone(2));
}

async function laneMain() {
  if (!need.main) return;
  if (!built(tagHEAD)) { notes.push("build image HEAD ไม่สำเร็จ → ข้อ 4–8 ส่วนที่ต้องเปิดระบบได้ 0"); return; }
  const head = await tree("HEAD");
  const sut = new Sut(ctx, "main");
  // ฐาน "ใช้งานจริง" = init ของระบบตั้งต้น + prod-data
  const init = join(W, "init-prod");
  mkdirSync(init, { recursive: true });
  for (const f of readdirSync(join(P.base, "db", "init"))) cpSync(join(P.base, "db", "init", f), join(init, f));
  cpSync(join(EXREF, KEY.prodData), join(init, "03-prod-data.sql"));
  await sut.startDb(init);
  // ① migration 2 ครั้ง (ก่อนเปิดเว็บ)
  const migDir = join(head, "db", "migrations");
  const ups = existsSync(migDir) ? readdirSync(migDir).filter((f) => /\.sql$/i.test(f) && !/down|rollback|revert|undo/i.test(f)).sort() : [];
  const mig = [];
  for (const round of [1, 2]) for (const f of ups) {
    const r = await sut.sqlFile(readFileSync(join(migDir, f), "utf8"));
    mig.push({ round, file: f, code: r.code, err: r.code ? (r.err || r.out).slice(-300) : "" });
    log(`migration รอบ ${round} ${f} → exit ${r.code}`);
  }
  raw.migrations = mig;
  if (DONE[6]) {
    const ok = ups.length > 0 && mig.every((x) => x.code === 0);
    setRow(6, "mig", ok ? 2 : 0, ups.length ? mig.map((x) => `รอบ${x.round} ${x.file}=${x.code}${x.err ? " " + x.err : ""}`).join(" · ") : "ไม่พบไฟล์ใน db/migrations/");
  } else setRow(6, "mig", 0, notDone(6));
  await sut.startWeb(tagHEAD);
  // ก่อน reset: ① ข้อมูลเดิม · smoke
  if (DONE[6]) {
    const c = await sut.counts();
    const pre = await hidden(sut, "ex6-pre.mjs");
    const cOk = c.customer === 10 && c.booking === 18;
    const pOk = pre?.checks?.[0]?.ok === true;
    setRow(6, "data", (cOk ? 1 : 0) + (pOk ? 1 : 0), `ลูกค้า ${c.customer} นัด ${c.booking} (ต้อง 10/18) · ${pre?.checks?.[0]?.label ?? ""}: ${pOk ? "ผ่าน" : pre?.checks?.[0]?.detail ?? "ไม่ได้ผล"}`);
  } else setRow(6, "data", 0, notDone(6));
  if (DONE[8]) {
    if ((await S.show(REPO, HEAD, "tests/smoke.mjs")) !== null) {
      const c1 = await sut.counts();
      const r = await sut.node("tests/smoke.mjs", { mounts: [[head, "/w"]], tag: "sm", timeoutMs: 5 * 60_000 });
      const c2 = await sut.counts();
      raw.smokeMain = { code: r.code, before: c1, after: c2, tail: (r.out + r.err).split("\n").slice(-4).join(" ⏎ ").slice(0, 400) };
      log(`smoke บนระบบผู้สอบ → exit ${r.code} · แถว ${JSON.stringify(c1)} → ${JSON.stringify(c2)}`);
    }
  }
  // hidden API
  if (DONE[4]) H.ex4 = await hidden(sut, "ex4.mjs");
  if (DONE[5]) H.ex5 = await hidden(sut, "ex5.mjs");
  if (DONE[6]) H.ex6 = await hidden(sut, "ex6.mjs");
  if (DONE[7]) H.ex7 = await hidden(sut, "ex7.mjs");
  // hidden UI
  const specs = [];
  if (DONE[5]) specs.push("ex5.ui.spec.ts");
  if (DONE[7]) specs.push("ex7.ui.spec.ts");
  if (specs.length) {
    const ui = join(W, "hidden-ui");
    cpSync(join(P.base, "e2e-legacy"), ui, { recursive: true, filter: (s) => !/[\\/](\.git|node_modules|test-report)([\\/]|$)/.test(s) });
    rmSync(join(ui, "tests"), { recursive: true, force: true });
    mkdirSync(join(ui, "tests", "zz-hidden"), { recursive: true });
    cpSync(join(P.base, "e2e-legacy", "tests", "fixtures.ts"), join(ui, "tests", "fixtures.ts"));
    for (const s of specs) cpSync(join(HIDDEN, SET, s), join(ui, "tests", "zz-hidden", `${SET}-${s}`));
    const r = await sut.playwright(ui, P.nm, ["tests/zz-hidden", "--project=chromium", "--reporter=list,json"], { env: hiddenEnv, tag: "hui", jsonOut: "hidden-ui.json", timeoutMs: 20 * 60_000 });
    appendFileSync(join(OUT, "hidden.log"), `\n===== hidden UI (exit ${r.code})\n${r.out.slice(-6000)}\n`);
    const { tests } = pwSummary(r.report);
    H.ui = tests.map((t) => ({ id: (t.title.match(/\]\s*(\S+)/) ?? [])[1] ?? t.title, label: t.title, weight: Number((t.title.match(/\[w=([\d.]+)\]/) ?? [])[1] ?? 0), ok: t.status === "expected", detail: t.error }));
    log(`hidden UI: ${H.ui.filter((x) => x.ok).length}/${H.ui.length} ผ่าน`);
  }
  // ⑥ check-rules HEAD บนฐานที่ migrate แล้ว
  if (DONE[6]) { crRes.head = await runCheckRules(sut, head, "HEAD(⑥)"); }
  // ข้อ 8 ③ golden HEAD
  if (DONE[8]) {
    if (existsSync(join(head, "tests", "exam2", "run.mjs"))) {
      const r = await sut.node("tests/exam2/run.mjs", { mounts: [[head, "/w"]], tag: "g8", timeoutMs: 8 * 60_000 });
      const m = r.out.match(/(\d+)\s*\/\s*(\d+)/g);
      raw.goldenHead = { code: r.code, last: m ? m.at(-1) : null, tail: r.out.split("\n").slice(-3).join(" ⏎ ").slice(0, 300) };
      log(`golden HEAD บนโค้ดสุดท้าย → exit ${r.code}`);
    }
  }
  // ข้อ 7 เทสต์ของผู้สอบ
  if (DONE[7] && ownFiles.length) ownRes = await runLearnerTests(sut, await tree("EX7"), ownFiles, "own");
  // งานของ commit ที่ image = HEAD
  const g = groups.get(tagHEAD);
  if (g) for (const t of g.tasks) await t(sut);
  if (!o.keep) await sut.stop();
}

async function laneCommitGroups() {
  const jobs = [];
  for (const [tag, g] of groups) {
    if (tag === tagHEAD && need.main) continue;
    jobs.push((async () => {
      if (!built(tag)) { log(`ข้าม lane ${g.initFrom} (build ไม่สำเร็จ)`); return; }
      const d = await tree(g.initFrom);
      const sut = new Sut(ctx, g.initFrom.toLowerCase().replace(/[^a-z0-9]/g, ""));
      try {
        await sut.start(tag, join(d, "db", "init"));
        for (const t of g.tasks) await t(sut);
      } catch (e) { notes.push(`lane ${g.initFrom}: ${e.message}`); log(`lane ${g.initFrom} error: ${e.message}`); }
      if (!o.keep) await sut.stop();
    })());
  }
  await Promise.all(jobs);
}

async function laneE2E() {
  if (!need.e2e && !need.fresh) return;
  if (!built(tagHEAD)) return;
  const head = await tree("HEAD");
  const shards = !need.e2e ? [] : E2E_MODE === "quick" ? [["api", "chromium"]] : [["api", "chromium"], ["firefox"], ["webkit"]];
  const jobs = [];
  const results = [];
  const runShard = async (projects, i) => {
    const sut = new Sut(ctx, `e2e${i}`);
    try {
      await sut.start(tagHEAD, join(head, "db", "init"));
      if (i === 0 && need.fresh) H.fresh = await hidden(sut, "ex6-fresh.mjs");
      if (!projects) return;
      const dir = join(W, `e2e-${i}`);
      cpSync(join(head, "e2e-legacy"), dir, { recursive: true, filter: (s) => !/[\\/](node_modules|test-report|out)([\\/]|$)/.test(s.slice(head.length)) });
      const r = await sut.playwright(dir, P.nm, [...projects.map((p) => `--project=${p}`), "--reporter=list,json"], { tag: "e2e", jsonOut: "e2e.json", timeoutMs: 40 * 60_000 });
      const s = pwSummary(r.report).sum;
      results.push({ projects, code: r.code, ...s });
      writeFileSync(join(OUT, `e2e-${projects.join("+")}.log`), r.out.slice(-20000));
      log(`e2e-legacy ${projects.join("+")} → ${s.passed} passed (expected-fail ${s.expectedFail}) · ${s.failed} failed · flaky ${s.flaky}`);
    } catch (e) { notes.push(`e2e ${projects?.join("+") ?? "fresh"}: ${e.message}`); log(`e2e lane error: ${e.message}`); }
    if (!o.keep) await sut.stop();
  };
  if (shards.length) shards.forEach((p, i) => jobs.push(runShard(p, i)));
  else jobs.push(runShard(null, 0));
  await Promise.all(jobs);
  if (shards.length && results.length === shards.length) {
    raw.e2e = results.reduce((a, r) => ({ passed: a.passed + r.passed, expectedFail: a.expectedFail + r.expectedFail, failed: a.failed + r.failed, flaky: a.flaky + r.flaky, skipped: a.skipped + r.skipped, failedTitles: [...a.failedTitles, ...r.failedTitles] }),
      { passed: 0, expectedFail: 0, failed: 0, flaky: 0, skipped: 0, failedTitles: [] });
    raw.e2e.mode = E2E_MODE;
  }
}

// build ทุก image ที่ต้องใช้ (ขนาน) · lane ของระบบตั้งต้น/mutant เริ่มพร้อมกันได้เลย
const baseLane = timed("lane-base", () => laneBase());
await timed("build", async () => {
  const want = new Map();
  if (tagHEAD) want.set(tagHEAD, "HEAD");
  for (const [tag, g] of groups) if (!want.has(tag)) want.set(tag, g.initFrom);
  const res = await Promise.all([...want].map(async ([tag, k]) => {
    const d = await tree(k);
    const r = await ensureImage(tag, join(d, "web"), join(d, "db", "init"), log);
    return [tag, k, r];
  }));
  raw.builds = res.map(([tag, k, r]) => ({ tag, from: k, ok: r.ok, cached: r.cached, s: sec(r.ms), err: r.err }));
  for (const [tag, k, r] of res) if (!r.ok) notes.push(`build image จาก ${k} ไม่สำเร็จ: ${(r.err ?? "").split("\n").slice(-3).join(" ")}`);
});
const built = (tag) => (raw.builds ?? []).find((b) => b.tag === tag)?.ok;

await timed("lanes", () => Promise.all([baseLane, timed("lane-main", () => laneMain()), timed("lane-commits", () => laneCommitGroups()), timed("lane-e2e", () => laneE2E())]));

// ───────────── รวมคะแนน ─────────────
// ข้อ 4
if (DONE[4]) setRow(4, "hidden", H.ex4?.score ?? 0, H.ex4 ? failList(H.ex4.checks, () => true) || "ผ่านทุกเคส" : "ไม่ได้ผล hidden test");
else setRow(4, "hidden", 0, notDone(4));
for (const n of [4, 5, 7]) if (DONE[n] && C[`EX${n}`]) {
  const c = crRes[n];
  setRow(n, "cr", c && c.code === 0 ? 1 : 0, c ? `${c.passed}/${c.total}${c.failed ? " · ล้ม: " + c.failed : ""}` : "ไม่ได้รัน");
}
// ข้อ 5
if (DONE[5]) {
  setRow(5, "hidden-api", H.ex5?.score ?? 0, H.ex5 ? failList(H.ex5.checks, () => true) || "ผ่านทุกเคส" : "ไม่ได้ผล");
  const ui = (H.ui ?? []).filter((x) => /^[AB]5-u/.test(x.id));
  setRow(5, "hidden-ui", sumChecks(ui, () => true), ui.length ? ui.filter((x) => !x.ok).map((x) => `${x.id}: ${x.detail.split("\n")[0]}`).join(" | ") || "ผ่านทุกเคส" : "ไม่ได้รัน");
  if (SET === "B") setRow(5, "evidence", H.evidence?.score ?? 0, H.evidence ? failList(H.evidence.checks, () => true) || "ตรงทุกฟิลด์" : "ไม่มี exam/EX5-EVIDENCE.json");
  if (!C["EX5-red"]) setRow(5, "red", 0, "ไม่มี commit EX5-red");
  else if (!redFiles.length) setRow(5, "red", 0, "EX5-red ไม่มีไฟล์เทสต์ที่เปลี่ยน");
  else {
    const red = redRes && redRes.some((x) => x.code !== 0 && x.code !== 404);
    const green = greenRes && greenRes.every((x) => x.code === 0);
    setRow(5, "red", red && green ? 1 : 0, `ไฟล์: ${redFiles.join(", ")} · บนโค้ดเดิม: ${redRes ? redRes.map((x) => `${x.file}=${x.code}`).join(" ") : "ไม่ได้รัน"} (ต้องแดง) · ที่ EX5: ${greenRes ? greenRes.map((x) => `${x.file}=${x.code}`).join(" ") : "ไม่ได้รัน"} (ต้องเขียว)`);
  }
} else for (const k of ["hidden-api", "hidden-ui", "evidence", "red"]) setRow(5, k, 0, notDone(5));
// ข้อ 6
if (DONE[6]) {
  const ch = H.ex6?.checks ?? [];
  for (const n of [2, 3, 4]) setRow(6, `s${n}`, sumChecks(ch, (c) => c.id.startsWith(`${SET}6-${n}`)), failList(ch, (c) => c.id.startsWith(`${SET}6-${n}`)) || (H.ex6 ? "ผ่าน" : "ไม่ได้ผล"));
  const s5 = sumChecks(ch, (c) => c.id.startsWith(`${SET}6-5`)) + sumChecks(H.fresh?.checks ?? [], () => true);
  setRow(6, "s5", s5, [failList(ch, (c) => c.id.startsWith(`${SET}6-5`)), H.fresh ? failList(H.fresh.checks, () => true) : "ติดตั้งใหม่: ไม่ได้รัน"].filter(Boolean).join(" | ") || "ผ่าน");
  const c = crRes.head;
  setRow(6, "cr", c && c.code === 0 ? 2 : 0, c ? `${c.passed}/${c.total}${c.failed ? " · ล้ม: " + c.failed : ""}` : "ไม่ได้รัน");
} else for (const k of ["s2", "s3", "s4", "s5", "cr"]) setRow(6, k, 0, notDone(6));
// ข้อ 7
if (DONE[7]) {
  setRow(7, "api", H.ex7?.score ?? 0, H.ex7 ? failList(H.ex7.checks, () => true) || "ผ่านทุกเคส" : "ไม่ได้ผล");
  const ui = (H.ui ?? []).filter((x) => /^[AB]7-u/.test(x.id));
  setRow(7, "ui", sumChecks(ui, () => true), ui.length ? ui.filter((x) => !x.ok).map((x) => `${x.id}: ${x.detail.split("\n")[0]}`).join(" | ") || "ผ่านทุกเคส" : "ไม่ได้รัน");
  const kinds = [ownFiles.some((f) => /\.spec\.ts$|\.test\.ts$/.test(f)) ? "Playwright" : null, ownFiles.some((f) => /\.(mjs|js|cjs)$/.test(f)) ? "API/node" : null].filter(Boolean);
  setRow(7, "own", ownRes && ownRes.length && ownRes.every((x) => x.code === 0) ? 1 : 0, ownFiles.length ? `${ownRes ? ownRes.map((x) => `${x.file}=${x.code}`).join(" ") : "ไม่ได้รัน"} · ชนิด: ${kinds.join("+") || "-"}${kinds.length < 2 ? " ⚠️ โจทย์ขอทั้ง API และ Playwright (ผู้สอนพิจารณา)" : ""}` : "EX7 ไม่มีไฟล์เทสต์ที่เพิ่ม/แก้");
  const steps = (await S.show(REPO, C.EX7, "exam/EX7-STEPS.md")) !== null;
  const msg = CM.log.find((x) => x.h === C.EX7)?.s ?? "";
  row(7, "steps").detail = `EX7-STEPS.md: ${steps ? "มี" : "ไม่มี"} · ข้อความ commit: "${msg.slice(0, 120)}" · check-rules เปลี่ยนใน EX6..EX7: ${(raw.caseDiffs[7]?.changed ?? []).join(" ") || "ไม่มี"}`;
} else for (const k of ["api", "ui", "own"]) setRow(7, k, 0, notDone(7));
// ข้อ 8
if (DONE[8]) {
  const gh = raw.goldenHead;
  setRow(8, "golden", gh && gh.code === 0 ? 2 : 0, gh ? `exit ${gh.code} ${gh.last ?? ""}` : "ไม่มี tests/exam2/run.mjs ที่ HEAD");
  const sm = raw.smokeMain, sb = raw.smokeBase;
  if (sm) {
    const same = sm.before && sm.after && sm.before.customer === sm.after.customer && sm.before.booking === sm.after.booking && sm.before.pointTxn === sm.after.pointTxn;
    const ok = sm.code === 0 && sb && sb.code !== 0 && same;
    setRow(8, "smoke", ok ? 2 : 0, `ระบบผู้สอบ exit ${sm.code} (ต้อง 0) · ระบบตั้งต้น exit ${sb?.code ?? "-"} (ต้อง ≠ 0) · แถว ${JSON.stringify(sm.before)} → ${JSON.stringify(sm.after)}${same ? "" : " ⚠️ ข้อมูลเปลี่ยน"}`);
  } else setRow(8, "smoke", 0, "ไม่มี tests/smoke.mjs ที่ HEAD");
  const reg = await S.show(REPO, HEAD, "exam/REGRESSION.md");
  if (!reg) setRow(8, "regr", 0, "ไม่มี exam/REGRESSION.md");
  else if (!raw.e2e) { const r = row(8, "regr"); r.score = null; r.detail = `ไม่ได้รัน e2e-legacy (โหมด ${E2E_MODE}) → ผู้สอนเทียบเอง`; r.kind = "teacher"; }
  else {
    const crH = crRes.head ?? crRes[7];
    const m = S.regressionMatches(reg, { e2e: raw.e2e, checkRules: crH && crH.total ? crH : null });
    const ok = m.passed && m.failed && m.expectedFail && (m.checkRules ?? true);
    if (E2E_MODE !== "full") { const r = row(8, "regr"); r.kind = "teacher"; }
    setRow(8, "regr", E2E_MODE !== "full" ? null : ok ? 3 : 0, `${E2E_MODE !== "full" ? "โหมด quick (api+chromium) → ผู้สอนเทียบเอง · " : ""}เครื่องตรวจได้ e2e ${raw.e2e.passed} passed · expected-fail ${raw.e2e.expectedFail} · ${raw.e2e.failed} failed${raw.e2e.flaky ? ` · flaky ${raw.e2e.flaky}` : ""} (${E2E_MODE}) · check-rules ${crH ? `${crH.passed}/${crH.total}` : "-"} · พบใน REGRESSION.md: ${Object.entries(m).map(([k, v]) => `${k}=${v ? "✓" : "✗"}`).join(" ")}`);
  }
} else for (const k of ["regr", "golden", "smoke"]) setRow(8, k, 0, notDone(8));

// กติกาหักคะแนน → ต่อข้อ
const itemAuto = {};
for (let n = 1; n <= 8; n++) {
  const sum = R.filter((r) => r.item === n && r.kind === "auto").reduce((a, r) => a + (r.score ?? 0), 0);
  const gate = n === 2 && row(2, "gate").detail.startsWith("❌") ? 0 : 1;
  const f = penalties.filter((p) => p.item === n).reduce((a, p) => Math.min(a, p.factor), 1);
  itemAuto[n] = { raw: Math.round(sum * 100) / 100, factor: f * gate, final: Math.round(sum * f * gate * 100) / 100 };
}
const autoTotal = Math.round(Object.values(itemAuto).reduce((a, x) => a + x.final, 0) * 100) / 100;
const elapsed = sec(Date.now() - T0);

// ───────────── รายงาน ─────────────
const csvEsc = (s) => `"${String(s ?? "").replace(/"/g, '""').replace(/\r?\n/g, " ")}"`;
const csv = ["item,key,criterion,kind,max,score,detail", ...R.map((r) => [r.item, r.key, csvEsc(r.label), r.kind === "auto" ? "auto" : "instructor", r.max, r.score ?? "", csvEsc(r.detail)].join(","))];
for (let n = 1; n <= 8; n++) csv.push([n, "item-total-auto", csvEsc(`รวมอัตโนมัติข้อ ${n} (หลังกติกาหัก ×${itemAuto[n].factor})`), "auto", R.filter((r) => r.item === n && r.kind === "auto").reduce((a, r) => a + r.max, 0), itemAuto[n].final, csvEsc(penalties.filter((p) => p.item === n).map((p) => p.why).join(" · "))].join(","));
csv.push(["all", "auto-total", csvEsc("รวมอัตโนมัติ"), "auto", 84, autoTotal, csvEsc(`เวลาตรวจ ${elapsed} วินาที`)].join(","));
writeFileSync(join(OUT, "score.csv"), "﻿" + csv.join("\r\n") + "\r\n");

const md = [];
md.push(`# ผลตรวจอัตโนมัติ · ${ID} · ชุด ${SET} v${VAR.v}`, "");
md.push(`| | |`, `|---|---|`);
md.push(`| ส่งมา | \`${SUB}\` |`, `| ตรวจเมื่อ | ${new Date().toISOString()} |`, `| เวลาตรวจ (wall-clock) | **${Math.floor(elapsed / 60)} นาที ${elapsed % 60} วินาที** (${Object.entries(timings).map(([k, v]) => `${k} ${v}s`).join(" · ")}) |`);
md.push(`| e2e-legacy | ${E2E_MODE} |`, `| **คะแนนอัตโนมัติ** | **${autoTotal} / 84** |`, `| คะแนนผู้สอน | ช่องว่าง (เต็ม 16) |`, "");
if (notes.length) md.push("**หมายเหตุ**", "", ...notes.map((n) => `- ${n}`), "");
if (penalties.length) md.push("**กติกาหักคะแนน (อัตโนมัติ · ผู้สอนยืนยัน)**", "", ...penalties.map((p) => `- ข้อ ${p.item}: ×${p.factor} · ${p.why}`), "");
md.push("| ข้อ | รายการ | ตรวจโดย | เต็ม | ได้ | รายละเอียด |", "|---|---|---|---|---|---|");
for (const r of R) md.push(`| ${r.item} | ${r.label} | ${r.kind === "auto" ? "เครื่อง" : "**ผู้สอน**"} | ${r.max} | ${r.score ?? "  "} | ${String(r.detail ?? "").replace(/\|/g, "\\|").replace(/\n/g, " ").slice(0, 600)} |`);
md.push("", "| ข้อ | อัตโนมัติ (ก่อนหัก) | ตัวคูณ | อัตโนมัติ | ผู้สอน | รวม |", "|---|---|---|---|---|---|");
for (let n = 1; n <= 8; n++) md.push(`| ${n} | ${itemAuto[n].raw} | ×${itemAuto[n].factor} | **${itemAuto[n].final}** | ___ / ${ITEM_MAX[n] - R.filter((r) => r.item === n && r.kind === "auto").reduce((a, r) => a + r.max, 0)} | ___ / ${ITEM_MAX[n]} |`);
md.push(`| รวม | | | **${autoTotal} / 84** | ___ / 16 | ___ / 100 |`, "");
md.push(`ข้อ 4–7 อัตโนมัติรวม ${Math.round((itemAuto[4].final + itemAuto[5].final + itemAuto[6].final + itemAuto[7].final) * 100) / 100} / 49 (เกณฑ์ผ่าน: รวม ≥ 60 และข้อ 4–7 รวม ≥ 30/58)`, "");
md.push("**ไฟล์ที่ต้องส่ง**", "", "| ข้อ | ไฟล์ | ที่ commit ของข้อ | ที่ HEAD |", "|---|---|---|---|");
for (const f of raw.files ?? []) md.push(`| ${f.item} | \`${f.path}\`${f.optional ? " (ทางเลือก)" : ""} | ${f.atCommit === null ? "ไม่มี commit" : f.atCommit ? "✓" : "✗"} | ${f.atHead ? "✓" : "✗"} |`);
writeFileSync(join(OUT, "score.md"), md.join("\n") + "\n");
writeFileSync(join(OUT, "raw.json"), JSON.stringify({ id: ID, set: SET, variant: VAR, commits: C, done: DONE, timings, elapsed, itemAuto, autoTotal, penalties, notes, H, crRes, redRes, greenRes, ownRes, raw }, null, 2));
const sumCsv = join(dirname(OUT), "results.csv");
if (!existsSync(sumCsv)) writeFileSync(sumCsv, "﻿id,set,variant,ex1,ex2,ex3,ex4,ex5,ex6,ex7,ex8,auto_total,seconds,graded_at\r\n");
appendFileSync(sumCsv, [ID, SET, VAR.v, ...[1, 2, 3, 4, 5, 6, 7, 8].map((n) => itemAuto[n].final), autoTotal, elapsed, new Date().toISOString()].join(",") + "\r\n");

// ปิดของตัวเอง
if (!o.keep) {
  const ps = await sh("docker", ["ps", "-aq", "--filter", `name=^${PREFIX}-${ID}-`]);
  const ids = ps.out.split("\n").filter(Boolean);
  if (ids.length) await sh("docker", ["rm", "-f", ...ids]);
  await sh("docker", ["network", "rm", ctx.net]);
  // image ของผู้สอบ (ไม่ลบ image ฐาน/mutant)
  const keepTags = new Set([P.baseTag, ...Object.values(P.mutTags)]);
  const mine = [...new Set([tagHEAD, ...Object.values(commitTags)].filter(Boolean))].filter((t) => !keepTags.has(t));
  if (mine.length) await sh("docker", ["rmi", "-f", ...mine]);
  await S.git(REPO, ["worktree", "prune"]);
}
log(`เสร็จ · อัตโนมัติ ${autoTotal}/84 · ${elapsed} วินาที · ${join(OUT, "score.md")}`);
