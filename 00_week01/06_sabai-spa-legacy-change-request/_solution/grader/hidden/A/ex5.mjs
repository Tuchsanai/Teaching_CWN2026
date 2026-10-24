// ข้อ 5 ชุด A · ติ๊กรถแต่ไม่มีโรงแรม/ระยะ · hidden ฝั่ง API 4 คะแนน (ฝั่งหน้าจอ 3 อยู่ใน ex5.ui.spec.ts) · EXAM-KEY §6
import { Score, reset, guest, login, Client, expectEq, all, GUEST } from "../lib.mjs";

const MSG = { th: "กรุณาเลือกโรงแรมหรือใส่ระยะทาง", en: "Please choose a hotel or enter the distance", zh: "请选择酒店或输入距离" };
const body = { type: "single", serviceCode: "S01", date: "2026-10-20", time: "10:00", wantTransport: true, ...GUEST };
const s = new Score(5, "hidden-api");
await reset();

await s.check("A5-a1", "/api/price wantTransport ไม่มีระยะ → 422 TRANSPORT_DISTANCE_REQUIRED", 1, async () => {
  const r = await guest().post("/api/price", body);
  return all(expectEq(r.status, 422, "status"), expectEq(r.json.error, "TRANSPORT_DISTANCE_REQUIRED", "error"));
});
await s.check("A5-a2", "/api/bookings wantTransport ไม่มีระยะ → 422 (ไม่บันทึก)", 1, async () => {
  const r = await guest().post("/api/bookings", { ...body, quotedTotal: 1000 });
  return all(expectEq(r.status, 422, "status"), expectEq(r.json.error, "TRANSPORT_DISTANCE_REQUIRED", "error"));
});
await s.check("A5-a3", "แพ็กเกจ P01 wantTransport ไม่มีระยะ → 422", 0.5, async () => {
  const r = await (await login("U08")).post("/api/price", { type: "package", serviceCode: "P01", people: 2, date: "2026-10-16", time: "10:00", wantTransport: true });
  return all(expectEq(r.status, 422, "status"), expectEq(r.json.error, "TRANSPORT_DISTANCE_REQUIRED", "error"));
});
await s.check("A5-a4", "ข้อความ th/en/zh ตรงที่ตกลง", 1, async () => {
  const out = [];
  for (const lang of ["th", "en", "zh"]) {
    const r = await new Client(lang).post("/api/price", body);
    out.push(expectEq(r.json.message, MSG[lang], lang));
  }
  return all(...out);
});
await s.check("A5-a5", "ไม่ติ๊กรถ → จองได้ 201 · ติ๊กรถ + H04 → 200", 0.5, async () => {
  const c = guest();
  const q = await c.post("/api/price", { ...body, wantTransport: false });
  const b = await c.post("/api/bookings", { ...body, wantTransport: false, quotedTotal: q.json.total });
  const h = await guest().post("/api/price", { ...body, hotelCode: "H04" });
  return all(expectEq(q.status, 200, "price"), expectEq(b.status, 201, "bookings"), expectEq(h.status, 200, "price+H04"));
});
await reset();
s.done();
