// ข้อ 4 ชุด B · ค่าแต้มตาม VARIANT (pointValue) · hidden 7 คะแนน (EXAM-KEY §5)
//   unit check ใช้ web/lib/rules ของผู้สอบ (mount ที่ LEARNER) แบบเดียวกับ E45 ของ check-rules
import { V, Score, reset, login, expectEq, all } from "../lib.mjs";

const PV = V.pointValue;
const s = new Score(4, "hidden");
const single = (svc, extra = {}) => ({ type: "single", serviceCode: svc, date: "2026-10-20", time: "10:00", ...extra });
await reset();

await s.check("B4-1", `U05 (Gold) S01 แลก 1 → ฿${950 - PV}`, 1.25, async () => {
  const r = await (await login("U05")).post("/api/price", single("S01", { redeemBlocks: 1 }));
  return all(expectEq(r.json.total, 950 - PV, "total"), expectEq(r.json.pointsDiscount, PV, "pointsDiscount"));
});
await s.check("B4-2", `U06 (Platinum) S05 แลก 1 → ฿${720 - PV}`, 1.25, async () => {
  const r = await (await login("U06")).post("/api/price", single("S05", { redeemBlocks: 1 }));
  return all(expectEq(r.json.total, 720 - PV, "total"), expectEq(r.json.pointsDiscount, PV, "pointsDiscount"));
});
const g = { type: "group", serviceCode: "S01", people: 4, date: "2026-10-16", time: "10:00", redeemBlocks: 2, hotelCode: "H04" };
await s.check("B4-3", `U04 กลุ่ม 4 + แลก 2 + H04 → ฿${3900 - 2 * PV}`, 1, async () => {
  const r = await (await login("U04")).post("/api/price", g);
  return expectEq(r.json.total, 3900 - 2 * PV, "total");
});
await s.check("B4-4", "… + GC01 ฿2,000 → จ่ายเพิ่ม", 1, async () => {
  const r = await (await login("U04")).post("/api/price", { ...g, giftCardCode: "SABAI-GC-2000" });
  return all(expectEq(r.json.total, 3900 - 2 * PV, "total"), expectEq(r.json.giftcardPaid, 2000, "giftcardPaid"), expectEq(r.json.otherPaid, 1900 - 2 * PV, "otherPaid"));
});
await s.check("B4-5", "… แต้มที่จะได้ = 14", 0.5, async () => {
  const r = await (await login("U04")).post("/api/price", { ...g, giftCardCode: "SABAI-GC-2000" });
  return expectEq(r.json.pointsToEarn, 14, "pointsToEarn");
});
await s.check("B4-6", "unit: ยอด ฿80 แลก 2 ก้อน → ลด ฿80 ยอด ฿0 (ไม่ติดลบ)", 1, async () => {
  const R = await import((process.env.LEARNER || "/l") + "/web/lib/rules/index.ts");
  const d = R.redeemPoints(2, 200, 8000).discount;
  const p = R.calcPrice({ type: "single", unitPrice: 8000, people: 1, tierPct: 0, birthdayApplied: false, points: 200, redeemBlocks: 2, transport: null, giftCardBalance: null });
  const one = R.redeemPoints(1, 100, 100000).discount;
  return all(expectEq(d, 8000, "discount cap"), expectEq(p.price.total, 0, "total"), expectEq(one, PV * 100, "1 ก้อน (สตางค์)"));
});
for (const lang of ["th", "en", "zh"]) {
  await s.check(`B4-t-${lang}`, `ข้อความ book.points (${lang}) มี ${PV}`, 1 / 3, async () => {
    // ข้อความอยู่ขั้น 3 ของหน้าจอง (render ฝั่ง client) → อ่านจาก web/lib/i18n.ts ของผู้สอบตรง ๆ · สำรอง: ค้นใน HTML
    let text = null;
    try {
      const I = await import((process.env.LEARNER || "/l") + "/web/lib/i18n.ts");
      text = I.t(lang, "book.points");
    } catch { /* ใช้สำรอง */ }
    if (!text || text === "book.points") {
      const html = await (await login("U01", lang)).html("/book?service=S01&type=single");
      text = (html.match(/(แลกแต้ม \([^)]*\)|Redeem points \([^)]*\)|积分兑换（[^）]*）)/) ?? [null])[0];
    }
    if (!text) return "ไม่พบข้อความแลกแต้ม (i18n key book.points)";
    const has = new RegExp(`(^|[^0-9])${PV}([^0-9]|$)`).test(text) && !/(^|[^0-9])50([^0-9]|$)/.test(text);
    return has ? true : `ข้อความ "${text}"`;
  });
}
await reset();
s.done();
