// ข้อ 5 ชุด B · กดเสร็จก่อนเวลา · hidden API 4.5 คะแนน (หน้าตารางคิว 1.5 อยู่ใน ex5.ui.spec.ts) · EXAM-KEY §6
//   T = 2026-10-10 15:00 + completeAfterMin (นัด B06 ของ U01)
import { V, Score, reset, login, me, expectEq, all } from "../lib.mjs";

const X = Number(V.completeAfterMin);
export const iso = (offMin) => {
  const t = 15 * 60 + X + offMin;
  return `2026-10-10T${String(Math.floor(t / 60)).padStart(2, "0")}:${String(t % 60).padStart(2, "0")}:00+07:00`;
};
const MSG = { th: "ยังไม่ถึงเวลานัด กดเสร็จไม่ได้", en: "This appointment has not started yet", zh: "预约时间未到，无法完成" };
const s = new Score(5, "hidden-api");

await s.check("B5-1", `now = T−1 (${iso(-1)}) กดเสร็จ B06 → 422 NOT_STARTED`, 0.75, async () => {
  await reset(iso(-1));
  const r = await (await login("OWNER")).post("/api/admin/bookings/6/complete", {});
  return all(expectEq(r.status, 422, "status"), expectEq(r.json.error, "NOT_STARTED", "error"));
});
await s.check("B5-2", "ข้อความ th/en/zh ตรงที่ตกลง", 0.5, async () => {
  await reset(iso(-1));
  const out = [];
  for (const lang of ["th", "en", "zh"]) {
    const r = await (await login("OWNER", lang)).post("/api/admin/bookings/6/complete", {});
    out.push(expectEq(r.json.message, MSG[lang], lang));
  }
  return all(...out);
});
await s.check("B5-3", "T−1: U01 ไม่ได้แต้ม/ยอดสะสม (99 · ฿12,400)", 0.25, async () => {
  await reset(iso(-1));
  await (await login("OWNER")).post("/api/admin/bookings/6/complete", {});
  const m = await me("U01");
  return all(expectEq(m.points, 99, "points"), expectEq(m.lifetimeSpend, 12400, "lifetimeSpend"));
});
await s.check("B5-4", `now = T (${iso(0)}) กดเสร็จ B06 → 200 · แต้ม +9 · U01 108 · ฿13,350`, 1.5, async () => {
  await reset(iso(0));
  const r = await (await login("OWNER")).post("/api/admin/bookings/6/complete", {});
  const m = await me("U01");
  return all(expectEq(r.status, 200, "status"), expectEq(r.json.pointsEarned, 9, "pointsEarned"), expectEq(m.points, 108, "points"), expectEq(m.lifetimeSpend, 13350, "lifetimeSpend"));
});
await s.check("B5-5", "now seed กดเสร็จ B02 (17 ต.ค.) → 422 NOT_STARTED · U02 0 · ฿30,000 · platinum", 1, async () => {
  await reset();
  const r = await (await login("OWNER")).post("/api/admin/bookings/2/complete", {});
  const m = await me("U02");
  return all(expectEq(r.status, 422, "status"), expectEq(r.json.error, "NOT_STARTED", "error"), expectEq(m, { points: 0, lifetimeSpend: 30000, tier: "platinum" }, "U02"));
});
await s.check("B5-6", "B08 (completed แล้ว) → 422 NOT_CONFIRMED", 0.5, async () => {
  await reset();
  const r = await (await login("OWNER")).post("/api/admin/bookings/8/complete", {});
  return all(expectEq(r.status, 422, "status"), expectEq(r.json.error, "NOT_CONFIRMED", "error"));
});
await reset();
s.done();
