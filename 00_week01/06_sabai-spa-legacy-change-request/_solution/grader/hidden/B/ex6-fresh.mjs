// ข้อ 6 ชุด B ⑤ ส่วน "ติดตั้งใหม่" · ระบบจาก db/init ของ HEAD (ไม่รัน migration) ต้องมีวันลาเหมือนกัน
import { V, Score, guest } from "../lib.mjs";
const TC = V.leaveTherapist;
const s = new Score(6, "fresh");
await s.check("B6-5b", `ติดตั้งใหม่จาก db/init ของ HEAD → ${TC} ลา 15 ต.ค.`, 1, async () => {
  const r = await guest().get("/api/slots?service=S01&date=2026-10-15&type=single&people=1");
  const x = (r.json.slots ?? []).find((y) => y.time === "10:00");
  const t = x ? (x.therapists ?? []).map((y) => y.code) : null;
  return t && !t.includes(TC) && t.length === 5 ? true : `therapists = ${t} (status ${r.status})`;
});
s.done();
