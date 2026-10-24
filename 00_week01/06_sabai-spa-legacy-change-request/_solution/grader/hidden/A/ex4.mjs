// ข้อ 4 ชุด A · ค่ารถรับส่งตาม VARIANT (freeKm · feePerVehicle) · hidden 7 คะแนน (EXAM-KEY §5)
import { V, Score, reset, guest, login, expectEq, all } from "../lib.mjs";

const FREE = V.freeKm, FEE = V.feePerVehicle;
const feeAt = (km) => (km <= FREE ? 0 : FEE);
const tr = async (q) => {
  const r = await guest().get(`/api/transport?${new URLSearchParams(q)}`);
  return r.status === 200 ? { vehicles: r.json.vehicles, fee: r.json.fee } : { status: r.status, error: r.json.error };
};
const s = new Score(4, "hidden");
await reset();

// ขอบระยะ (2.5)
const W = 2.5 / 8;
await s.check("A4-d1", "H03 5.1 กม. 1 คน → ฟรี", W, async () => expectEq((await tr({ hotel: "H03", people: 1 })).fee, 0));
for (const km of ["7.0", "7.1", "8.0", "8.1"]) {
  await s.check(`A4-d-${km}`, `ระยะ ${km} กม. → ฿${feeAt(Number(km))}`, W, async () => expectEq((await tr({ distance: km, people: 1 })).fee, feeAt(Number(km))));
}
await s.check("A4-d6", "H04 12 กม. → ค่ารถต่อคัน", W, async () => expectEq((await tr({ hotel: "H04", people: 1 })).fee, FEE));
await s.check("A4-d7", "H05 15.0 กม. → ค่ารถต่อคัน (ยังรับ)", W, async () => expectEq((await tr({ hotel: "H05", people: 1 })).fee, FEE));
await s.check("A4-d8", "H06 15.1 กม. → 422 OUT_OF_AREA", W, async () => expectEq(await tr({ hotel: "H06", people: 1 }), { status: 422, error: "OUT_OF_AREA" }));

// หลายคัน (1)
await s.check("A4-v", "H04 5 คน → 2 คัน", 1, async () => expectEq(await tr({ hotel: "H04", people: 5 }), { vehicles: 2, fee: 2 * FEE }));

// แพ็กเกจ (1)
await s.check("A4-p", "P01 2 คน H04 → รถรวมในแพ็กเกจ ยอด ฿5,800", 1, async () => {
  const r = await (await login("U08")).post("/api/price", { type: "package", serviceCode: "P01", people: 2, date: "2026-10-16", time: "10:00", hotelCode: "H04" });
  return all(expectEq(r.status, 200, "status"), expectEq(r.json.total, 5800, "total"), expectEq(r.json.transportFee, 0, "transportFee"));
});

// รวมกับส่วนลด/แต้ม/บัตร (1.5)
const g = { type: "group", serviceCode: "S01", people: 4, date: "2026-10-16", time: "10:00", redeemBlocks: 2, hotelCode: "H04" };
await s.check("A4-c1", "U04 กลุ่ม 4 + แลก 200 แต้ม + H04", 0.75, async () => {
  const r = await (await login("U04")).post("/api/price", g);
  return all(expectEq(r.json.total, 3500 + FEE, "total"), expectEq(r.json.transportFee, FEE, "transportFee"));
});
await s.check("A4-c2", "… + บัตร GC01 ฿2,000", 0.75, async () => {
  const r = await (await login("U04")).post("/api/price", { ...g, giftCardCode: "SABAI-GC-2000" });
  return all(expectEq(r.json.total, 3500 + FEE, "total"), expectEq(r.json.giftcardPaid, 2000, "giftcardPaid"), expectEq(r.json.otherPaid, 1500 + FEE, "otherPaid"), expectEq(r.json.pointsToEarn, 15, "pointsToEarn"));
});

// ข้อความ 3 ภาษา (1)
for (const lang of ["th", "en", "zh"]) {
  await s.check(`A4-t-${lang}`, `ข้อความกฎค่ารถ (${lang}) มี ${FREE} กม. และ ${FEE}`, 1 / 3, async () => {
    const html = await guest(lang).html("/transport");
    const m = html.match(/data-testid="transport-rule"[^>]*>([\s\S]*?)<\/p>/);
    if (!m) return "ไม่พบ data-testid=transport-rule";
    const text = m[1].replace(/<[^>]+>/g, "").replace(/,/g, "");
    const hasKm = new RegExp(`(^|[^0-9.])${FREE}([^0-9]|$)`).test(text);
    const hasFee = new RegExp(`(^|[^0-9])${FEE}([^0-9]|$)`).test(text);
    return hasKm && hasFee ? true : `ข้อความ "${text.trim()}"`;
  });
}
await reset();
s.done();
