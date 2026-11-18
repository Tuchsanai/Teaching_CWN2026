// รันโจทย์ 26 เคสเดิมซ้ำ REPEAT รอบต่อโมเดล ผ่าน API ของเว็บ (POST /api/chat แบบไม่ stream) โดยไม่เปิดเบราว์เซอร์
// ใช้ cases.json และตัวตรวจ tests/check.ts ชุดเดิมทุกตัวอักษร -> repeat.json
//   REPEAT=5 CONCURRENCY=4 BASE_URL=http://host.docker.internal:3403 node repeat.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { runChecks } from "./tests/check.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const BASE_URL = process.env.BASE_URL || "http://host.docker.internal:3403";
const REPEAT = Number(process.env.REPEAT || 5);
const CONCURRENCY = Number(process.env.CONCURRENCY || 4);
const MODELS = ["base", "ft"];
const { cases } = JSON.parse(fs.readFileSync(path.join(here, "cases.json"), "utf8"));

// ข้อความของปุ่มลัดบนหน้าแชท (ตรงกับ components/Chat.tsx)
const CHIP_TEXT = {
  price: "ขอดูราคาบริการทั้งหมดหน่อยค่ะ",
  hours: "ร้านเปิดปิดกี่โมงคะ",
  backpain: "ปวดหลังมาก แนะนำนวดแบบไหนดีคะ",
  promo: "ตอนนี้มีโปรโมชันอะไรบ้างคะ",
  book: "อยากจองคิวนวดค่ะ",
};
// หน้าแชทแสดงคำตอบโดยตัด # หัวข้อ และ ** ออก -> ทำแบบเดียวกันให้ข้อความที่ตรวจตรงกับที่เทสต์เบราว์เซอร์เห็น
const shown = (t) => (t || "").replace(/^#{1,6}\s+/gm, "").replace(/\*\*/g, "").trim();

async function chat(session, message, model) {
  for (let attempt = 1; ; attempt++) {
    const res = await fetch(`${BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: session, message, model, stream: false }),
    });
    const j = await res.json().catch(() => ({}));
    if (res.ok) return j;
    if (attempt >= 3) throw new Error(`HTTP ${res.status} ${j.detail || j.error || ""}`);
    await new Promise((r) => setTimeout(r, 3000));
  }
}

async function runCase(c, model, round) {
  const session = `repeat-${model}-r${round}-case${c.id}-${Date.now().toString(36)}`;
  const turns = [];
  let booking = null;
  const failures = [];
  const step = async (s) => {
    const msg = s.chip ? CHIP_TEXT[s.chip] : s.type;
    const r = await chat(session, msg, model);
    turns.push({ user: s.chip ? `[กดปุ่ม ${s.chip}]` : msg, bot: shown(r.reply) });
    if (r.booking) booking = r.booking;
    if (r.booking_error) turns[turns.length - 1].booking_error = r.booking_error;
  };
  try {
    for (const s of c.steps) await step(s);
    if (c.booking) {
      for (const msg of c.confirm ?? []) {
        if (booking) break;
        await step({ type: msg });
      }
      const w = c.booking;
      if (!booking) failures.push("ไม่เห็นการ์ดจองสำเร็จ");
      else {
        if (!booking.customer_name.includes(w.name)) failures.push(`การ์ด: ชื่อไม่ใช่ ${w.name}`);
        if (!String(booking.phone).replace(/\D/g, "").includes(w.phone)) failures.push(`การ์ด: เบอร์ไม่ใช่ ${w.phone}`);
        if (!booking.service_name.includes(w.service)) failures.push(`การ์ด: บริการไม่ใช่ ${w.service}`);
        if (!booking.booking_time.includes(w.time)) failures.push(`การ์ด: วันเวลาไม่ใช่ ${w.time}`);
      }
    }
    failures.push(...runChecks(c.checks, turns.map((t) => t.bot)));
  } catch (e) {
    failures.push("เรียก API ไม่สำเร็จ: " + e.message);
  }
  return { id: c.id, passed: failures.length === 0, failures, turns, booking };
}

// คิวงานทั้งหมด (รอบ × โมเดล × เคส) รันพร้อมกันทีละ CONCURRENCY งาน
const jobs = [];
for (let round = 1; round <= REPEAT; round++)
  for (const model of MODELS) for (const c of cases) jobs.push({ round, model, c });
const done = [];
let next = 0;
const t0 = Date.now();
await Promise.all(
  Array.from({ length: CONCURRENCY }, async () => {
    while (next < jobs.length) {
      const j = jobs[next++];
      const r = await runCase(j.c, j.model, j.round);
      done.push({ ...j, r });
      process.stdout.write(`\r${done.length}/${jobs.length} งาน`);
    }
  })
);
console.log(` · ${Math.round((Date.now() - t0) / 1000)} วินาที`);

const out = { base_url: BASE_URL, repeat: REPEAT, total_cases: cases.length, models: {} };
for (const model of MODELS) {
  const rounds = [];
  for (let round = 1; round <= REPEAT; round++) {
    const rs = done.filter((d) => d.model === model && d.round === round).map((d) => d.r).sort((a, b) => a.id - b.id);
    rounds.push({ round, passed: rs.filter((r) => r.passed).length, failed_cases: rs.filter((r) => !r.passed).map((r) => r.id), results: rs });
  }
  const scores = rounds.map((r) => r.passed);
  const mean = scores.reduce((a, b) => a + b, 0) / scores.length;
  const sd = Math.sqrt(scores.reduce((a, b) => a + (b - mean) ** 2, 0) / scores.length);
  const per_case = cases.map((c) => ({
    id: c.id,
    slug: c.slug,
    pass_count: rounds.filter((r) => !r.failed_cases.includes(c.id)).length,
  }));
  out.models[model] = {
    scores,
    mean: +mean.toFixed(2),
    sd: +sd.toFixed(2),
    min: Math.min(...scores),
    max: Math.max(...scores),
    always_fail: per_case.filter((p) => p.pass_count === 0).map((p) => p.id),
    flaky: per_case.filter((p) => p.pass_count > 0 && p.pass_count < REPEAT).map((p) => p.id),
    per_case,
    rounds,
  };
  console.log(`${model}: ${scores.join(", ")} / ${cases.length} · เฉลี่ย ${mean.toFixed(2)} ± ${sd.toFixed(2)}`);
}
fs.writeFileSync(path.join(here, "repeat.json"), JSON.stringify(out, null, 2));
console.log("เขียน repeat.json แล้ว");
