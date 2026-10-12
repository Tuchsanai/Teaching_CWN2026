// ข้อ 6 ชุด A ⑤ ส่วน "ติดตั้งใหม่" · ระบบที่สร้างจาก db/init ของ HEAD (ไม่รัน migration) ต้องได้ S03 ปิดเหมือนกัน
import { Score, guest, expectEq, all } from "../lib.mjs";
const s = new Score(6, "fresh");
await s.check("A6-5b", "ติดตั้งใหม่จาก db/init ของ HEAD → S03 ปิด", 1, async () => {
  const c = ((await guest().get("/api/services")).json.services ?? []).map((x) => x.code);
  const r = await guest().get("/api/slots?service=S03&date=2026-10-20&type=single&people=1");
  return all(expectEq(c.includes("S03"), false, "services มี S03"), expectEq(c.includes("S01"), true, "services มี S01"), expectEq(r.status, 422, "slots S03"));
});
s.done();
