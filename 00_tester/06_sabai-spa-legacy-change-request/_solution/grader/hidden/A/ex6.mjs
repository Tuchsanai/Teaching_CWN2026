// ข้อ 6 ชุด A · ปิด S03 · ②③④ และ ⑤ ส่วน reset (EXAM-KEY §7) · รันหลังขั้น "ก่อน reset"
import { Score, reset, guest, login, expectEq, all, GUEST } from "../lib.mjs";

const s = new Score(6, "hidden");
const slotsS03 = () => guest().get("/api/slots?service=S03&date=2026-10-20&type=single&people=1");
const codes = async () => ((await guest().get("/api/services")).json.services ?? []).map((x) => x.code);
await reset();

// ② ลูกค้าไม่เห็น/จองไม่ได้ (2)
await s.check("A6-2a", "/api/services ไม่มี S03 (บริการอื่นยังอยู่)", 0.5, async () => {
  const c = await codes();
  return !c.includes("S03") && c.includes("S01") && c.includes("S05") ? true : `services = ${c.join(",")}`;
});
await s.check("A6-2b", "/api/slots S03 → 422 SERVICE_INVALID", 0.5, async () => {
  const r = await slotsS03();
  return all(expectEq(r.status, 422, "status"), expectEq(r.json.error, "SERVICE_INVALID", "error"));
});
await s.check("A6-2c", "/api/price S03 → 422 SERVICE_INVALID", 0.5, async () => {
  const r = await guest().post("/api/price", { type: "single", serviceCode: "S03", date: "2026-10-20", time: "10:00" });
  return all(expectEq(r.status, 422, "status"), expectEq(r.json.error, "SERVICE_INVALID", "error"));
});
await s.check("A6-2d", "/api/bookings S03 → 422 SERVICE_INVALID", 0.5, async () => {
  const r = await guest().post("/api/bookings", { type: "single", serviceCode: "S03", date: "2026-10-20", time: "13:00", quotedTotal: 1200, ...GUEST });
  return all(expectEq(r.status, 422, "status"), expectEq(r.json.error, "SERVICE_INVALID", "error"));
});

// ③ ระบบแนะนำไม่แนะนำ S03 (2)
await s.check("A6-3a", "ตัวเลือกอารมณ์ 4 แบบ ไม่มี S03", 0.5, async () => {
  const bad = [];
  for (const m of ["stressed", "tired", "aches", "insomnia"]) {
    const r = await guest().get(`/api/mood?mood=${m}`);
    const c = (r.json.services ?? []).map((x) => x?.code ?? null);
    if (r.status !== 200 || c.includes("S03")) bad.push(`${m}:${r.status}:${c.join("/")}`);
  }
  return bad.length ? bad.join(" ") : true;
});
await s.check("A6-3b", "แบบทดสอบ ทุกชุดคำตอบ ไม่แนะนำ S03", 0.5, async () => {
  const Q = (await guest().get("/api/quiz")).json.questions;
  const combos = Q.reduce((acc, q) => acc.flatMap((a) => q.options.map((o) => ({ ...a, [q.id]: o.value }))), [{}]);
  let bad = 0, n = 0;
  for (const a of combos) {
    const r = await guest().post("/api/quiz", { answers: a });
    n++;
    if (r.status !== 200 || r.json.code === "S03") bad++;
  }
  return bad === 0 ? true : `${bad}/${n} ชุดคำตอบแนะนำ S03 หรือ error`;
});
await s.check("A6-3c", "หน้าวิเคราะห์ผิว /skin ไม่มีบริการ S03", 0.5, async () => {
  const html = await guest().html("/skin");
  return /ประคบสมุนไพร|Herbal Compress|草药热敷/.test(html) ? "พบชื่อ S03 ใน /skin" : true;
});
await s.check("A6-3d", "แชท: ถามราคา/จองประคบ → ไม่เสนอราคาและไม่เข้าขั้นจอง S03", 0.5, async () => {
  const bad = [];
  for (const msg of ["ประคบสมุนไพรราคาเท่าไหร่", "จองประคบ", "herbal compress price"]) {
    const r = await guest().post("/api/chat", { message: msg });
    const reply = String(r.json.reply ?? "");
    if (r.status !== 200 || /1,?200/.test(reply) || /S03/.test(JSON.stringify(r.json.state ?? {}))) bad.push(`"${msg}" → ${r.status} ${reply.slice(0, 80)} ${JSON.stringify(r.json.state ?? {})}`);
  }
  return bad.length ? bad.join(" | ") : true;
});

// ④ เจ้าของร้านเปิด/ปิดได้ (2)
await s.check("A6-4a", "owner เปิด S03 → slots 200", 0.75, async () => {
  const o = await login("OWNER");
  const r = await o.post("/api/admin/services/S03", { active: true });
  return all(expectEq(r.status < 300, true, `POST open status ${r.status}`), expectEq((await slotsS03()).status, 200, "slots"));
});
await s.check("A6-4b", "owner ปิด S03 อีกครั้ง → slots 422", 0.75, async () => {
  const o = await login("OWNER");
  const r = await o.post("/api/admin/services/S03", { active: false });
  return all(expectEq(r.status < 300, true, `POST close status ${r.status}`), expectEq((await slotsS03()).status, 422, "slots"));
});
await s.check("A6-4c", "ลูกค้าเรียก admin/services → 403", 0.5, async () => expectEq((await (await login("U01")).post("/api/admin/services/S03", { active: true })).status, 403, "status"));

// ⑤ reset 2 ครั้ง (1) · ส่วนติดตั้งใหม่อยู่ใน ex6-fresh.mjs
await s.check("A6-5a", "reset 2 ครั้ง → 200 · S03 ยังปิด", 1, async () => {
  await reset(); await reset();
  const c = await codes();
  const r = await slotsS03();
  return all(expectEq(c.includes("S03"), false, "services มี S03"), expectEq(r.status, 422, "slots S03"));
});
await reset();
s.done();
