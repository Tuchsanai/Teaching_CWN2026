// ข้อ 6 ชุด B ① (ส่วน API) · ฐาน "ใช้งานจริง" หลัง migration 2 ครั้ง **ก่อน reset** · อ่านอย่างเดียว
import { Score, login } from "../lib.mjs";
const s = new Score(6, "pre");
await s.check("B6-1", "นัดวันที่ 12 ต.ค. ของ T02 (B15) T06 (B16) T03 (B01) ยังอยู่ในตารางคิว", 1, async () => {
  const r = await (await login("OWNER")).get("/api/admin/bookings?date=2026-10-12");
  const c = (r.json.bookings ?? []).map((b) => b.code);
  return ["B15", "B16", "B01"].every((x) => c.includes(x)) ? true : `คิว 12 ต.ค. = ${c.join(",")} (status ${r.status})`;
});
s.done();
