#!/usr/bin/env node
// สร้าง "งานส่ง" ปลอมสำหรับทดสอบเครื่องตรวจ (ชุด A) จากเฉลยอ้างอิง exam-ref/*.diff + ไฟล์ใน selftest/A/
//   node selftest/make-selftest.mjs --out <dir> [--variant 0|1] [--break 7] [--blank] [--work <grader work dir>]
//   --blank   = โฟลเดอร์ตั้งต้นที่ยังไม่ทำอะไร (ไม่มี .git) แบบที่ผู้เรียนแตกจาก zip
//   --break 7 = เฉลยครบ แต่ทำข้อ 7 พังโดยตั้งใจ (API คืนรายการเรียงเก่า → ใหม่)
// commit: EX0 … EX4 · EX5-red · EX5 · EX6 · EX7 · EX8 (golden ข้อ 2 อัดใหม่ใน EX8 ด้วยระบบของ EX7 ผ่าน docker)
import { parseArgs } from "node:util";
import { fileURLToPath } from "node:url";
import { dirname, join, resolve } from "node:path";
import { existsSync, mkdirSync, rmSync, cpSync, readFileSync, writeFileSync, appendFileSync } from "node:fs";
import { sh } from "../lib/sh.mjs";
import { Sut, ensureImage, ensureNetwork } from "../lib/docker.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const GRADER = resolve(HERE, "..");
const CHAPTER = resolve(GRADER, "..", "..");
const EXREF = resolve(GRADER, "..", "exam-ref");
const SRC = join(HERE, "A");
const { values: o } = parseArgs({ options: { out: { type: "string" }, variant: { type: "string" }, break: { type: "string" }, blank: { type: "boolean" }, prefix: { type: "string" }, regression: { type: "string" }, salt: { type: "string" }, "golden-from": { type: "string" } } });
const OUT = resolve(o.out);
const V = Number(o.variant ?? 0);
const VAR = JSON.parse(readFileSync(join(GRADER, "variants.json"), "utf8")).A[V];
const PREFIX = o.prefix ?? "exref-g";
rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });
for (const d of ["web", "db", "e2e-legacy"]) cpSync(join(CHAPTER, d), join(OUT, d), { recursive: true, filter: (s) => !/[\\/](node_modules|\.next|test-report)([\\/]|$)/.test(s.slice(CHAPTER.length)) });
if (o.blank) { console.log(`blank → ${OUT}`); process.exit(0); }

const git = async (...a) => {
  const r = await sh("git", ["-c", "core.autocrlf=false", "-c", "user.name=selftest", "-c", "user.email=selftest@local", "-C", OUT, ...a]);
  if (r.code !== 0) throw new Error(`git ${a.join(" ")}: ${r.err}${r.out}`);
  return r.out;
};
const commit = async (msg) => { await git("add", "-A"); await git("commit", "-q", "--allow-empty", "-m", msg); console.log("commit", msg); };
const apply = (diff) => git("apply", "--3way", "--whitespace=nowarn", join(EXREF, diff).replace(/\\/g, "/"));
const put = (rel, srcRel) => { mkdirSync(dirname(join(OUT, rel)), { recursive: true }); cpSync(join(SRC, srcRel), join(OUT, rel)); };

mkdirSync(join(OUT, "exam"), { recursive: true });
writeFileSync(join(OUT, "exam", "VARIANT.json"), JSON.stringify(VAR) + "\n");
// --salt: ไฟล์เล็กใน web/ ทำให้ทุก tree ไม่ซ้ำ image/cache ที่เคย build (ใช้วัดเวลาตรวจแบบ build จริง)
if (o.salt) writeFileSync(join(OUT, "web", "salt.txt"), `selftest salt ${o.salt}\n`);
await git("init", "-q");
await git("config", "core.autocrlf", "false");
await commit("EX0: base");
put("exam/Q1.json", "exam/Q1.json");
await commit("EX1: อ่านและอธิบาย repo");
await apply("A-2.diff");
put("tests/exam2/README.md", "tests/exam2-README.md");
await commit("EX2: golden master /api/price");
put("exam/IMPACT.md", "exam/IMPACT.md");
await commit("EX3: impact Lotus Suite");
await apply(V === 0 ? "A-4-v0.diff" : "A-4.diff");
put("exam/ORACLE-CHANGES.md", "exam/ORACLE-4.md");
await commit("EX4: ค่ารถใหม่ตาม VARIANT");
put("tests/exam5/transport-required.mjs", "tests/exam5-transport-required.mjs");
await commit("EX5-red: ทำซ้ำเรื่องรถ (แดงบนโค้ดเดิม)");
await apply("A-5.diff");
put("exam/BUGFIX.md", "exam/BUGFIX.md");
appendFileSync(join(OUT, "exam", "ORACLE-CHANGES.md"), readFileSync(join(SRC, "exam", "ORACLE-5.md"), "utf8"));
await commit("EX5: บังคับระยะเมื่อติ๊กรถ (UI + API)");
await apply("A-6.diff");
put("exam/MIGRATION.md", "exam/MIGRATION.md");
await commit("EX6: service.active + ปิด S03");
await apply("A-7.diff");
put("tests/exam7/points-history.mjs", "tests/exam7-points-history.mjs");
put("tests/exam7/points-history.spec.ts", "tests/exam7-points-history.spec.ts");
put("exam/EX7-STEPS.md", "exam/EX7-STEPS.md");
if (o.break === "7") {
  // พังโดยตั้งใจ: คืนรายการเรียงเก่า → ใหม่ (ไม่ reverse)
  const f = join(OUT, "web", "lib", "server", "customer.ts");
  const s = readFileSync(f, "utf8");
  const t = s.replace("items: items.reverse() }", "items }");
  if (s === t) throw new Error("break 7: ไม่พบจุดที่จะแก้");
  writeFileSync(f, t);
}
await commit("EX7: ประวัติแต้ม — API → เทสต์ API → หน้า /account → Playwright");

// EX8: อัด golden ใหม่บนระบบของ EX7 (ค่าที่ข้อ 4 เปลี่ยน) แล้วเขียน ORACLE ของ golden
if (o["golden-from"]) {
  cpSync(join(resolve(o["golden-from"]), "tests", "exam2", "golden"), join(OUT, "tests", "exam2", "golden"), { recursive: true });
} else {
const ctx = { prefix: PREFIX, id: "selftest", net: `${PREFIX}-selftest-net`, log: (m) => console.log(m) };
await ensureNetwork(ctx.net);
const tag = `${PREFIX}-web:selftest-${Date.now()}`;
const b = await ensureImage(tag, join(OUT, "web"), join(OUT, "db", "init"), ctx.log);
if (!b.ok) throw new Error("build: " + b.err);
const sut = new Sut(ctx, "rec");
await sut.start(tag, join(OUT, "db", "init"));
const r = await sut.node("tests/exam2/run.mjs", { mounts: [[OUT, "/w"]], args: ["--record"] });
console.log("record →", r.code);
await sut.stop();
await sh("docker", ["rmi", "-f", tag]);
await sh("docker", ["network", "rm", ctx.net]);
}
const changed = (await git("diff", "--name-only", "--", "tests/exam2/golden")).split("\n").filter(Boolean).map((f) => f.replace(/^.*\//, "").replace(/\.json$/, ""));
let rows = "";
for (const g of changed) rows += `| golden \`${g}\` | ค่าเดิมตามระบบตั้งต้น | อัดใหม่หลังกฎค่ารถใหม่ | ข้อ 4 |\n`;
appendFileSync(join(OUT, "exam", "ORACLE-CHANGES.md"), rows);
put("tests/smoke.mjs", "tests/smoke.mjs");
put("RELEASE-NOTES.md", "RELEASE-NOTES.md");
const [ep, eef, ef] = (o.regression ?? "113,4,1").split(",").map(Number);
writeFileSync(join(OUT, "exam", "REGRESSION.md"), `# REGRESSION (โค้ดสุดท้าย)

| ชุด | คำสั่ง | ผล |
|---|---|---|
| check-rules | \`node web/scripts/check-rules.mjs\` | 90/90 |
| golden ข้อ 2 | \`node tests/exam2/run.mjs\` | 29/29 |
| เทสต์ข้อ 5 | \`node tests/exam5/transport-required.mjs\` | 1/1 |
| เทสต์ข้อ 7 | \`node tests/exam7/points-history.mjs\` + Playwright | 2/2 |
| e2e-legacy 4 project (api chromium firefox webkit) | \`npx playwright test --project=api --project=chromium --project=firefox --project=webkit\` | ${ep} passed (expected-fail ${eef}) · ${ef} failed (TC-SEC-05 ล้มตั้งแต่ก่อนแก้) |
`);
await commit(`EX8: regression + ส่งมอบ (golden อัดใหม่ ${changed.length} ไฟล์)`);
console.log(`เสร็จ → ${OUT}`);
