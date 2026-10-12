// ข้อ 6 ชุด A ① (ส่วน API) · รันบนฐาน "ใช้งานจริง" หลัง migration 2 ครั้ง **ก่อน reset** · อ่านอย่างเดียว
import { Score, login } from "../lib.mjs";
const s = new Score(6, "pre");
await s.check("A6-1", "นัด S03 ของลูกค้าจริง (B14 · 20 ต.ค.) ยังอยู่ในตารางคิว", 1, async () => {
  const r = await (await login("OWNER")).get("/api/admin/bookings?date=2026-10-20");
  const b = (r.json.bookings ?? []).find((x) => x.code === "B14");
  if (!b) return `ไม่พบ B14 (status ${r.status})`;
  return b.serviceCode === "S03" && b.status === "confirmed" ? true : `B14 = ${b.serviceCode} ${b.status}`;
});
s.done();
