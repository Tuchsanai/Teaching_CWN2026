// ข้อ 7 ชุด A · ประวัติแต้ม GET /api/me/points · hidden API 10 คะแนน (EXAM-KEY §8)
// หมายเหตุ: date ของรายการที่เพิ่งสร้าง = เวลาเครื่องจริง (created_at DEFAULT now()) → ตรวจแค่รูปแบบ ไม่เทียบวัน
import { Score, reset, guest, login, Client, USERS, expectEq, all } from "../lib.mjs";

const LBL = {
  th: { earn: "ได้จากการใช้บริการ", redeem: "แลกเป็นส่วนลด", refund: "คืนจากการยกเลิก", opening: "ยอดยกมา" },
  en: { earn: "Earned from service", redeem: "Redeemed for discount", refund: "Refunded from cancellation", opening: "Opening balance" },
  zh: { earn: "消费获得", redeem: "兑换折扣", refund: "取消退还", opening: "期初余额" },
};
const pick = (it) => ({ date: it?.date, bookingCode: it?.bookingCode ?? null, points: it?.points, reason: it?.reason, balanceAfter: it?.balanceAfter });
const hist = async (c) => (await c.get("/api/me/points"));
const isDate = (d) => typeof d === "string" && /^\d{4}-\d{2}-\d{2}$/.test(d);
const s = new Score(7, "hidden-api");
await reset();

await s.check("A7-1", "U01: balance 99 · [earn +19 B13 2026-09-30 → 99] [opening +80 → 80]", 2, async () => {
  const r = await hist(await login("U01"));
  if (r.status !== 200) return `status ${r.status}`;
  return all(
    expectEq(r.json.balance, 99, "balance"),
    expectEq((r.json.items ?? []).map(pick), [
      { date: "2026-09-30", bookingCode: "B13", points: 19, reason: "earn", balanceAfter: 99 },
      { date: "2026-01-15", bookingCode: null, points: 80, reason: "opening", balanceAfter: 80 },
    ], "items"),
  );
});
await s.check("A7-2", "ป้าย reasonLabel 3 ภาษา (earn/opening)", 1, async () => {
  const out = [];
  for (const lang of ["th", "en", "zh"]) {
    const r = await hist(await login("U01", lang));
    out.push(expectEq((r.json.items ?? []).map((x) => x.reasonLabel), [LBL[lang].earn, LBL[lang].opening], lang));
  }
  return all(...out);
});

// จอง (แลก 200) → ยกเลิก
const g = { type: "group", serviceCode: "S01", people: 4, date: "2026-10-16", time: "10:00", redeemBlocks: 2, hotelCode: "H04" };
let bk = null;
await s.check("A7-3", "U04 จองกลุ่ม แลก 200 แต้ม → [0] redeem −200 รหัสนัดใหม่ · คงเหลือ 50", 1.5, async () => {
  await reset();
  const u = await login("U04");
  const q = await u.post("/api/price", g);
  const b = await u.post("/api/bookings", { ...g, quotedTotal: q.json.total });
  if (b.status !== 201) return `จองไม่ได้ ${b.status} ${b.json.error}`;
  bk = { id: b.json.bookingId, code: b.json.code, u };
  const r = await hist(u);
  const it = (r.json.items ?? [])[0];
  return all(expectEq(r.json.balance, 50, "balance"), expectEq(pick(it).bookingCode, bk.code, "bookingCode"), expectEq(it?.points, -200, "points"),
    expectEq(it?.reason, "redeem", "reason"), expectEq(it?.balanceAfter, 50, "balanceAfter"), expectEq(isDate(it?.date), true, "date YYYY-MM-DD"));
});
await s.check("A7-4", "ยกเลิกนัดนั้น → [refund +200 → 250] [redeem −200 → 50] [opening +250 → 250]", 1.5, async () => {
  if (!bk) return "ไม่มีนัดจาก A7-3";
  const c = await bk.u.post(`/api/bookings/${bk.id}/cancel`);
  if (c.status !== 200) return `ยกเลิก ${c.status} ${c.json.error}`;
  const r = await hist(bk.u);
  const items = (r.json.items ?? []).map((x) => ({ bookingCode: x.bookingCode ?? null, points: x.points, reason: x.reason, balanceAfter: x.balanceAfter }));
  return all(expectEq(r.json.balance, 250, "balance"), expectEq(items, [
    { bookingCode: bk.code, points: 200, reason: "refund", balanceAfter: 250 },
    { bookingCode: bk.code, points: -200, reason: "redeem", balanceAfter: 50 },
    { bookingCode: null, points: 250, reason: "opening", balanceAfter: 250 },
  ], "items"));
});
await s.check("A7-5", "ป้าย redeem/refund ภาษาไทย", 0.5, async () => {
  if (!bk) return "ไม่มีนัดจาก A7-3";
  const r = await hist(bk.u);
  return expectEq((r.json.items ?? []).slice(0, 2).map((x) => x.reasonLabel), [LBL.th.refund, LBL.th.redeem], "labels");
});

await s.check("A7-6", "ทุกบัญชี U01–U08: Σ points = balance = แต้มใน /api/me · balanceAfter ต่อเนื่อง", 1.5, async () => {
  await reset();
  const bad = [];
  for (const u of Object.keys(USERS).filter((k) => k !== "OWNER")) {
    const c = await login(u);
    const r = await hist(c);
    const items = r.json.items ?? [];
    const sum = items.reduce((a, x) => a + x.points, 0);
    const mePts = (await c.get("/api/me")).json.points;
    let run = 0, chain = true;
    for (const x of [...items].reverse()) { run += x.points; if (x.balanceAfter !== run) chain = false; }
    if (r.status !== 200 || sum !== r.json.balance || r.json.balance !== mePts || !chain) bad.push(`${u}: status ${r.status} Σ${sum} balance ${r.json.balance} me ${mePts} chain ${chain}`);
  }
  return bad.length ? bad.join(" · ") : true;
});
await s.check("A7-7", "U03 ไม่มีรายการ (items [] · balance 0) · owner items []", 1, async () => {
  const a = await hist(await login("U03"));
  const o = await hist(await login("OWNER"));
  return all(expectEq(a.json.items, [], "U03 items"), expectEq(a.json.balance, 0, "U03 balance"), expectEq(o.status === 200 ? o.json.items : [], [], "owner items"));
});
await s.check("A7-8", "ไม่ล็อกอิน → 401", 1, async () => expectEq((await hist(guest())).status, 401, "status"));
await reset();
s.done();
