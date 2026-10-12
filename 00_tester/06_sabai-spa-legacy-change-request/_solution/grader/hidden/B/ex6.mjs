// ข้อ 6 ชุด B · วันลานักบำบัด (leaveTherapist ลา 15 ต.ค.) · ②③④ และ ⑤ ส่วน reset (EXAM-KEY §7)
import { V, Score, reset, guest, book, expectEq, all } from "../lib.mjs";

const TC = V.leaveTherapist;
const s = new Score(6, "hidden");
const slotTh = async (date, time = "10:00") => {
  const r = await guest().get(`/api/slots?service=S01&date=${date}&type=single&people=1`);
  const x = (r.json.slots ?? []).find((y) => y.time === time);
  return x ? (x.therapists ?? []).map((t) => t.code) : null;
};
await reset();

// ② คิวว่างไม่นับคนที่ลา (2)
await s.check("B6-2a", `slots S01 15 ต.ค. 10:00 ไม่มี ${TC} (เหลือ 5 คน)`, 1, async () => {
  const t = await slotTh("2026-10-15");
  return t && !t.includes(TC) && t.length === 5 ? true : `therapists = ${t}`;
});
await s.check("B6-2b", `slots S01 16 ต.ค. 10:00 มี ${TC} (6 คน)`, 1, async () => {
  const t = await slotTh("2026-10-16");
  return t && t.includes(TC) && t.length === 6 ? true : `therapists = ${t}`;
});

// ③ จองระบุคนที่ลา (2)
await s.check("B6-3a", `จองระบุ ${TC} วันที่ 15 ต.ค. → 409 SLOT_TAKEN`, 1.5, async () => {
  await reset();
  const r = await book(guest(), { type: "single", serviceCode: "S01", date: "2026-10-15", time: "10:00", therapists: [TC] });
  return all(expectEq(r.status, 409, "status"), expectEq(r.json.error, "SLOT_TAKEN", "error"));
});
await s.check("B6-3b", `จองระบุ ${TC} วันที่ 16 ต.ค. → 201`, 0.5, async () => {
  await reset();
  const r = await book(guest(), { type: "single", serviceCode: "S01", date: "2026-10-16", time: "10:00", therapists: [TC] });
  return expectEq(r.status, 201, "status");
});

// ④ จัดคนอัตโนมัติข้ามคนที่ลา (2)
await s.check("B6-4a", "กลุ่ม S01 6 คน 15 ต.ค. 10:00 → 409", 0.75, async () => {
  await reset();
  const r = await book(guest(), { type: "group", serviceCode: "S01", people: 6, date: "2026-10-15", time: "10:00" });
  return expectEq(r.status, 409, "status");
});
await s.check("B6-4b", `กลุ่ม 5 คน 15 ต.ค. 10:00 → 201 ไม่มี ${TC}`, 0.75, async () => {
  await reset();
  const r = await book(guest(), { type: "group", serviceCode: "S01", people: 5, date: "2026-10-15", time: "10:00" });
  if (r.status !== 201) return `status ${r.status} ${r.json.error}`;
  const t = await slotTh("2026-10-15");
  // ทุกคนที่ไม่ลาถูกใช้หมด → รอบนั้นต้องไม่เหลือใคร (ถ้าเหลือ = จัดคนที่ลาเข้าไป)
  return !t || t.length === 0 ? true : `หลังจองกลุ่ม 5 คน ยังเหลือ ${t}`;
});
await s.check("B6-4c", "จองเดี่ยวอัตโนมัติ 15 ต.ค. 16:00 × 6 → 5 ครั้งแรก 201 ครั้งที่ 6 → 409", 0.5, async () => {
  await reset();
  const st = [];
  for (let i = 0; i < 6; i++) st.push((await book(guest(), { type: "single", serviceCode: "S01", date: "2026-10-15", time: "16:00" })).status);
  return expectEq(st, [201, 201, 201, 201, 201, 409], "status");
});

// ⑤ reset 2 ครั้ง (1) · ส่วนติดตั้งใหม่อยู่ใน ex6-fresh.mjs
await s.check("B6-5a", "reset 2 ครั้ง → 200 · วันลายังอยู่", 1, async () => {
  await reset(); await reset();
  const t = await slotTh("2026-10-15");
  return t && !t.includes(TC) && t.length === 5 ? true : `therapists = ${t}`;
});
await reset();
s.done();
