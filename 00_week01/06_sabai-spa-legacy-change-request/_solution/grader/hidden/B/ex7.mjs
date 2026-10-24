// ข้อ 7 ชุด B · รีวิวนักบำบัด POST /api/reviews · hidden API 10 คะแนน (EXAM-KEY §8)
//   bookingId: ลองแบบตัวเลข (id ใน /api/me/bookings) ก่อน ถ้าไม่ได้ 201 ลองรหัส "B13" แล้วใช้รูปแบบที่ได้ตลอดไฟล์
import { V, Score, reset, guest, login, expectEq, all } from "../lib.mjs";

const USER = V.reviewUser, BK = V.reviewBooking, STARS = V.reviewStars;
const EXP = { 0: { th: "T03", rating: "4.5", min45: 4 }, 1: { th: "T05", rating: "4.0", min45: 2 }, 2: { th: "T03", rating: "4.3", min45: 3 } }[V.v];
const idOf = (code, form) => (form === "num" ? Number(code.slice(1)) : code);
let FORM = "num";
const post = async (c, code, stars) => c.post("/api/reviews", { bookingId: idOf(code, FORM), stars });
const rating = async (code) => {
  const r = await guest().get("/api/therapists");
  const t = (r.json.therapists ?? []).find((x) => x.code === code);
  return t ? String(t.rating) : null;
};
const min45 = async () => ((await guest().get("/api/therapists?min=4.5")).json.therapists ?? []).length;
const s = new Score(7, "hidden-api");

await reset();
let created = false;
await s.check("B7-1", `${USER} รีวิว ${BK} ${STARS} ดาว → 201`, 1.5, async () => {
  const u = await login(USER);
  let r = await post(u, BK, STARS);
  if (r.status !== 201) { FORM = "code"; r = await post(u, BK, STARS); }
  created = r.status === 201;
  return created ? true : `status ${r.status} ${r.json.error ?? ""} (ลองทั้ง id ตัวเลขและรหัส)`;
});
await s.check("B7-2", `คะแนน ${EXP.th} อัปเดตทันที → ${EXP.rating}`, 2, async () => expectEq(await rating(EXP.th), EXP.rating, "rating"));
await s.check("B7-3", `/api/therapists?min=4.5 → ${EXP.min45} คน`, 1, async () => expectEq(await min45(), EXP.min45, "count"));
await s.check("B7-4", "รีวิวซ้ำ → 409 ALREADY_REVIEWED", 1, async () => {
  if (!created) return "รีวิวแรกไม่สำเร็จ";
  const r = await post(await login(USER), BK, STARS);
  return all(expectEq(r.status, 409, "status"), expectEq(r.json.error, "ALREADY_REVIEWED", "error"));
});

await s.check("B7-5", "stars 0 / 6 / 4.5 / \"5\" / null → 422", 1, async () => {
  await reset();
  const u = await login("U01");
  const bad = [];
  for (const st of [0, 6, 4.5, "5", null]) {
    const r = await post(u, "B13", st);
    if (r.status !== 422) bad.push(`${JSON.stringify(st)}→${r.status}`);
  }
  return bad.length ? bad.join(" ") : true;
});
await s.check("B7-6", "U01 รีวิว B05 (ยังไม่เสร็จ) → 422 NOT_COMPLETED", 1, async () => {
  await reset();
  const r = await post(await login("U01"), "B05", 5);
  return all(expectEq(r.status, 422, "status"), expectEq(r.json.error, "NOT_COMPLETED", "error"));
});
await s.check("B7-7", "U02 รีวิวนัด B13 ของคนอื่น → 403", 0.75, async () => {
  await reset();
  return expectEq((await post(await login("U02"), "B13", 5)).status, 403, "status");
});
await s.check("B7-8", "ไม่ล็อกอิน → 401", 0.75, async () => expectEq((await post(guest(), "B13", 5)).status, 401, "status"));
await s.check("B7-9", "นัดคู่ B02 / กลุ่ม B04 (หลายนักบำบัด) ที่เสร็จแล้ว → 422", 1, async () => {
  await reset("2026-10-17T21:00:00+07:00");
  const o = await login("OWNER");
  const c2 = await o.post("/api/admin/bookings/2/complete", {});
  const c4 = await o.post("/api/admin/bookings/4/complete", {});
  if (c2.status !== 200 || c4.status !== 200) return `กดเสร็จไม่ได้ B02 ${c2.status} B04 ${c4.status}`;
  const r2 = await post(await login("U02"), "B02", 5);
  const r4 = await post(await login("U08"), "B04", 5);
  return all(expectEq(r2.status, 422, "B02"), expectEq(r4.status, 422, "B04"));
});
await reset();
s.done();
