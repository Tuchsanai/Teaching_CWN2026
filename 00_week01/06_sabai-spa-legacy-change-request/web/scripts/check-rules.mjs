// ตรวจกฎร้านตามตาราง E01–E90 ของ TEST-DATA.md
//   ใช้: node scripts/check-rules.mjs            (ค่าเริ่มต้น BASE_URL=http://localhost:4000)
//        $env:BASE_URL="http://localhost:4000"; node scripts/check-rules.mjs
// - reset ก่อนทุกเคส (POST /api/test/reset {now}) ใช้ now ตามแถว
// - เคสที่เป็น unit test เรียกฟังก์ชันใน lib/rules ตรง (Node ≥ 22.18 รัน .ts ได้เลย)
// - ค่าที่คาดหวังทุกตัวมาจาก TEST-DATA.md / REQUIREMENTS.md (ห้ามแก้ให้ตรงกับโค้ด)

const BASE = (process.env.BASE_URL || "http://localhost:4000").replace(/\/$/, "");
const DEFAULT_NOW = "2026-10-10T10:00:00+07:00";

const USERS = {
  U01: ["nida@sabai.test", "Nida@2026"],
  U02: ["ton@sabai.test", "Ton@2026"],
  U03: ["may@sabai.test", "May@2026"],
  U04: ["fon@sabai.test", "Fon@2026"],
  U05: ["prae@sabai.test", "Prae@2026"],
  U06: ["vipa@sabai.test", "Vipa@2026"],
  U07: ["kan@sabai.test", "Kan@2026"],
  U08: ["liwei@sabai.test", "LiWei@2026"],
  OWNER: ["owner@sabai.test", "Owner@2026"],
};

const MSG = {
  SLOT_TAKEN: "เวลานี้ถูกจองแล้ว",
  GROUP_CALL_SHOP: "กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน",
  OUT_OF_AREA: "อยู่นอกพื้นที่รับส่ง",
  GC_EXPIRED: "บัตรหมดอายุแล้ว",
};

// ── HTTP client ที่จำ cookie ──────────────────────────────────────────────
class Client {
  constructor() {
    this.cookie = "";
  }
  async req(method, path, body) {
    const headers = { "Content-Type": "application/json", "Accept-Language": "th" };
    if (this.cookie) headers.Cookie = this.cookie;
    const r = await fetch(BASE + path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
    const set = r.headers.get("set-cookie");
    if (set) {
      const m = set.match(/sabai_session=([^;]*)/);
      if (m) this.cookie = `sabai_session=${m[1]}`;
    }
    let json = null;
    const text = await r.text();
    try {
      json = JSON.parse(text);
    } catch {
      json = { raw: text };
    }
    return { status: r.status, json };
  }
  get(p) {
    return this.req("GET", p);
  }
  post(p, b = {}) {
    return this.req("POST", p, b);
  }
}

async function login(user) {
  const c = new Client();
  const [email, password] = USERS[user];
  const r = await c.post("/api/auth/login", { email, password });
  if (r.status !== 200) throw new Error(`login ${user} failed: ${r.status}`);
  return c;
}

const guest = () => new Client();
const GUEST = { contactName: "ผู้ทดสอบ", contactPhone: "0899999999" };

async function reset(now = DEFAULT_NOW) {
  const r = await guest().post("/api/test/reset", { now });
  if (r.status !== 200 || !r.json.ok) throw new Error(`reset failed: ${r.status} ${JSON.stringify(r.json)}`);
}

// ── ตัวช่วยตรวจ ───────────────────────────────────────────────────────────
class Check {
  constructor() {
    this.fails = [];
    this.count = 0;
  }
  eq(actual, expected, label) {
    this.count++;
    const ok = typeof expected === "number" && typeof actual === "number" ? Math.abs(actual - expected) < 0.001 : JSON.stringify(actual) === JSON.stringify(expected);
    if (!ok) this.fails.push(`${label}: ได้ ${JSON.stringify(actual)} ควรเป็น ${JSON.stringify(expected)}`);
    return ok;
  }
  ok(cond, label) {
    this.count++;
    if (!cond) this.fails.push(label);
    return !!cond;
  }
}

const e90 = { checked: 0, mismatches: [] };
let owner = null;

/** ราคา → จองด้วย quotedTotal เดียวกับหน้าสรุป → อ่าน total_amount จาก db ผ่านตารางคิว (E90) */
async function quoteAndBook(c, body, ck, label) {
  const q = await c.post("/api/price", body);
  if (q.status !== 200) {
    ck.ok(false, `${label}: /api/price ${q.status} ${q.json.error ?? ""}`);
    return { quote: q, booking: null };
  }
  const b = await c.post("/api/bookings", { ...body, quotedTotal: q.json.total });
  if (b.status !== 201) {
    ck.ok(false, `${label}: /api/bookings ${b.status} ${b.json.error ?? ""}`);
    return { quote: q, booking: b };
  }
  const row = await dbRow(body.date, b.json.code);
  e90.checked++;
  if (!row || Math.abs(row.total - q.json.total) > 0.001) e90.mismatches.push(`${label} (${b.json.code}): สรุป ${q.json.total} · db ${row?.total}`);
  return { quote: q, booking: b, row };
}

async function dbRow(date, code) {
  owner = owner ?? (await login("OWNER"));
  const r = await owner.get(`/api/admin/bookings?date=${date}`);
  return r.json.bookings?.find((x) => x.code === code) ?? null;
}

const slotsOf = async (q) => {
  const r = await guest().get(`/api/slots?${new URLSearchParams(q)}`);
  return r;
};
const times = (r) => (r.json.slots ?? []).map((s) => s.time);
const avail = (r, t) => (r.json.slots ?? []).find((s) => s.time === t)?.available === true;
const book = (c, body) => c.post("/api/price", body).then((q) => (q.status === 200 ? c.post("/api/bookings", { ...body, quotedTotal: q.json.total }) : q));

// ── รายการเคส ─────────────────────────────────────────────────────────────
const cases = [];
const T = (id, title, fn, opts = {}) => cases.push({ id, title, fn, ...opts });

let R; // lib/rules (โหลดตอนเริ่ม)

T("E01", "BR-01 ไม่มีรอบ 09:30", async (ck) => {
  const r = await slotsOf({ service: "S01", date: "2026-10-11", type: "single", people: 1 });
  ck.ok(!times(r).includes("09:30"), "slots ต้องไม่มี 09:30");
  const b = await guest().post("/api/bookings", { type: "single", serviceCode: "S01", date: "2026-10-11", time: "09:30", ...GUEST, quotedTotal: 1000 });
  ck.eq(b.status, 422, "จอง 09:30 status");
});
T("E02", "BR-01 รอบแรก 10:00", async (ck) => {
  const r = await slotsOf({ service: "S01", date: "2026-10-11", type: "single", people: 1 });
  ck.eq(times(r)[0], "10:00", "รอบแรก");
  ck.ok(avail(r, "10:00"), "10:00 ว่าง");
});
T("E03", "BR-01 10:15 ไม่ลงช่วง 30 นาที", async (ck) => {
  const b = await guest().post("/api/bookings", { type: "single", serviceCode: "S01", date: "2026-10-11", time: "10:15", ...GUEST, quotedTotal: 1000 });
  ck.eq(b.status, 422, "status");
  ck.ok(!times(await slotsOf({ service: "S01", date: "2026-10-11", type: "single", people: 1 })).includes("10:15"), "slots ไม่มี 10:15");
});
T("E04", "BR-01 S02 เริ่ม 20:00", async (ck) => {
  ck.ok(avail(await slotsOf({ service: "S02", date: "2026-10-11", type: "single", people: 1 }), "20:00"), "มีรอบ 20:00");
});
T("E05", "BR-01 S02 เริ่ม 20:30 จบ 22:00 พอดี", async (ck) => {
  ck.ok(avail(await slotsOf({ service: "S02", date: "2026-10-11", type: "single", people: 1 }), "20:30"), "มีรอบ 20:30");
  ck.eq((await book(guest(), { type: "single", serviceCode: "S02", date: "2026-10-11", time: "20:30", ...GUEST })).status, 201, "จอง 20:30");
});
T("E06", "BR-01 S02 เริ่ม 21:00 ไม่มีรอบ", async (ck) => {
  ck.ok(!times(await slotsOf({ service: "S02", date: "2026-10-11", type: "single", people: 1 })).includes("21:00"), "ไม่มี 21:00");
  const b = await guest().post("/api/bookings", { type: "single", serviceCode: "S02", date: "2026-10-11", time: "21:00", ...GUEST, quotedTotal: 1400 });
  ck.eq(b.status, 422, "จอง 21:00 status");
});
T("E07", "BR-01 S01 เริ่ม 21:00 จบ 22:00 พอดี", async (ck) => {
  ck.ok(avail(await slotsOf({ service: "S01", date: "2026-10-11", type: "single", people: 1 }), "21:00"), "มีรอบ 21:00");
  ck.eq((await book(guest(), { type: "single", serviceCode: "S01", date: "2026-10-11", time: "21:00", ...GUEST })).status, 201, "จอง 21:00");
});
T("E08", "BR-01 S01 เริ่ม 21:30 ไม่มีรอบ", async (ck) => {
  ck.ok(!times(await slotsOf({ service: "S01", date: "2026-10-11", type: "single", people: 1 })).includes("21:30"), "ไม่มี 21:30");
  const b = await guest().post("/api/bookings", { type: "single", serviceCode: "S01", date: "2026-10-11", time: "21:30", ...GUEST, quotedTotal: 1000 });
  ck.eq(b.status, 422, "จอง 21:30 status");
});
T("E09", "BR-01 P01 120 นาที 20:00 ✅ / 20:30 ❌", async (ck) => {
  const r = await slotsOf({ service: "P01", date: "2026-10-11", type: "package", people: 1 });
  ck.ok(avail(r, "20:00"), "มี 20:00");
  ck.ok(!times(r).includes("20:30"), "ไม่มี 20:30");
});

const t03 = (time) => ({ type: "single", serviceCode: "S01", date: "2026-10-12", time, therapists: ["T03"], ...GUEST });
T("E10", "BR-02 13:30 ซ้อนท้าย", async (ck) => {
  const b = await book(guest(), t03("13:30"));
  ck.eq(b.status, 409, "status");
  ck.eq(b.json.message, MSG.SLOT_TAKEN, "ข้อความ");
});
T("E11", "BR-02 14:30 ซ้อนกลาง ไม่บันทึก", async (ck) => {
  const b = await book(guest(), t03("14:30"));
  ck.eq(b.status, 409, "status");
  ck.eq(b.json.message, MSG.SLOT_TAKEN, "ข้อความ");
  owner = owner ?? (await login("OWNER"));
  const q = await owner.get("/api/admin/bookings?date=2026-10-12");
  ck.eq(q.json.bookings.length, 1, "คิววันที่ 12 ยังมีแค่ B01");
});
T("E12", "BR-02 15:00 ต่อกันพอดี", async (ck) => ck.eq((await book(guest(), t03("15:00"))).status, 201, "status"));
T("E13", "BR-02 15:30", async (ck) => ck.eq((await book(guest(), t03("15:30"))).status, 201, "status"));
T("E14", "NFR-12 กดจองพร้อมกัน 2 คำขอ", async (ck) => {
  const [a, b] = await Promise.all([login("U03"), login("U04")]);
  const body = { type: "single", serviceCode: "S01", date: "2026-10-15", time: "11:00", therapists: ["T04"], quotedTotal: 1000 };
  const res = await Promise.all([a.post("/api/bookings", body), b.post("/api/bookings", body)]);
  const st = res.map((r) => r.status).sort();
  ck.eq(st, [201, 409], "status ทั้งสองคำขอ");
  const lost = res.find((r) => r.status === 409);
  ck.eq(lost?.json.message, MSG.SLOT_TAKEN, "ข้อความคำขอที่แพ้");
});

T("E15", "BR-03 วันนี้ (+0)", async (ck) => {
  ck.eq((await slotsOf({ service: "S01", date: "2026-10-10", type: "single", people: 1 })).status, 422, "slots status");
  ck.eq((await guest().post("/api/bookings", { type: "single", serviceCode: "S01", date: "2026-10-10", time: "16:00", ...GUEST, quotedTotal: 1000 })).status, 422, "จอง status");
});
T("E16", "BR-03 พรุ่งนี้ (+1)", async (ck) => ck.eq((await slotsOf({ service: "S01", date: "2026-10-11", type: "single", people: 1 })).status, 200, "status"));
T("E17", "BR-03 +30 วัน", async (ck) => {
  ck.eq((await slotsOf({ service: "S01", date: "2026-11-09", type: "single", people: 1 })).status, 200, "status");
  ck.eq((await book(guest(), { type: "single", serviceCode: "S01", date: "2026-11-09", time: "10:00", ...GUEST })).status, 201, "จอง 9 พ.ย.");
});
T("E18", "BR-03 +31 วัน", async (ck) => {
  ck.eq((await slotsOf({ service: "S01", date: "2026-11-10", type: "single", people: 1 })).status, 422, "slots status");
  ck.eq((await guest().post("/api/bookings", { type: "single", serviceCode: "S01", date: "2026-11-10", time: "10:00", ...GUEST, quotedTotal: 1000 })).status, 422, "จอง status");
});

T("E19", "BR-04 จองคู่ 1 / 2 / 3 คน", async (ck) => {
  const c = await login("U02");
  const base = { type: "couple", serviceCode: "S02", date: "2026-10-20", time: "19:00" };
  ck.eq((await c.post("/api/price", { ...base, people: 1 })).status, 422, "1 คน");
  ck.eq((await c.post("/api/price", { ...base, people: 3 })).status, 422, "3 คน");
  ck.eq((await book(c, { ...base, people: 2 })).status, 201, "2 คน");
});
T("E20", "BR-04 Couple Suite คู่ที่ 2 รอบ 19:00 / 19:30 / 20:30", async (ck) => {
  const c = await login("U04");
  const base = { type: "couple", serviceCode: "S02", people: 2, date: "2026-10-17" };
  const a = await book(c, { ...base, time: "19:00" });
  ck.eq(a.status, 409, "19:00 status");
  ck.eq(a.json.message, MSG.SLOT_TAKEN, "19:00 ข้อความ");
  const b = await book(c, { ...base, time: "19:30" });
  ck.eq(b.status, 409, "19:30 status");
  ck.eq(b.json.message, MSG.SLOT_TAKEN, "19:30 ข้อความ");
  ck.eq((await book(c, { ...base, time: "20:30" })).status, 201, "20:30");
});
T("E21", "BR-04 นักบำบัดว่างแค่ 1 คน", async (ck) => {
  const c = await login("U02");
  ck.ok(!avail(await slotsOf({ service: "S01", date: "2026-10-14", type: "couple", people: 2 }), "16:00"), "slots คู่ 16:00 ไม่ว่าง");
  ck.eq((await book(c, { type: "couple", serviceCode: "S01", people: 2, date: "2026-10-14", time: "16:00" })).status, 409, "จองคู่");
  const s = await book(c, { type: "single", serviceCode: "S01", date: "2026-10-14", time: "16:00" });
  ck.eq(s.status, 201, "จองเดี่ยว");
  ck.eq(s.json.therapists, ["T06"], "ได้ T06");
});
T("E22", "BR-05 กลุ่ม 2 คน", async (ck) => {
  ck.eq((await guest().post("/api/price", { type: "group", serviceCode: "S01", people: 2, date: "2026-10-16", time: "10:00" })).status, 422, "status");
});
T("E23", "BR-05 กลุ่ม 3 / 6 คน", async (ck) => {
  const c = await login("U08");
  ck.eq((await book(c, { type: "group", serviceCode: "S01", people: 3, date: "2026-10-16", time: "10:00" })).status, 201, "3 คน");
  await reset();
  ck.eq((await book(await login("U08"), { type: "group", serviceCode: "S01", people: 6, date: "2026-10-16", time: "10:00" })).status, 201, "6 คน");
});
T("E24", "BR-05 กลุ่ม 7 คน", async (ck) => {
  const r = await guest().post("/api/price", { type: "group", serviceCode: "S01", people: 7, date: "2026-10-16", time: "10:00" });
  ck.eq(r.status, 422, "status");
  ck.eq(r.json.message, MSG.GROUP_CALL_SHOP, "ข้อความ");
  ck.ok(typeof r.json.phone === "string" && r.json.phone.length > 0, "มีเบอร์ร้าน");
});
T("E25", "BR-05 กลุ่ม 6 คน นักบำบัดไม่พอ", async (ck) => {
  const c = await login("U08");
  ck.eq((await book(c, { type: "group", serviceCode: "S01", people: 6, date: "2026-10-13", time: "10:00" })).status, 409, "6 คน 10:00");
  ck.eq((await book(c, { type: "group", serviceCode: "S01", people: 5, date: "2026-10-13", time: "10:00" })).status, 201, "5 คน 10:00");
  await reset();
  ck.eq((await book(await login("U08"), { type: "group", serviceCode: "S01", people: 6, date: "2026-10-13", time: "11:30" })).status, 201, "6 คน 11:30");
});

const grp = (n, extra = {}) => ({ type: "group", serviceCode: "S01", people: n, date: "2026-10-16", time: "10:00", ...extra });
T("E26", "BR-06 กลุ่ม 3 คน ฿3,000", async (ck) => {
  const r = await quoteAndBook(await login("U08"), grp(3), ck, "E26");
  ck.eq(r.quote.json.total, 3000, "ยอด");
});
T("E27", "BR-06 กลุ่ม 4 คน ฿3,600", async (ck) => ck.eq((await quoteAndBook(await login("U08"), grp(4), ck, "E27")).quote.json.total, 3600, "ยอด"));
T("E28", "BR-06 กลุ่ม 5 คน ฿4,500", async (ck) => ck.eq((await quoteAndBook(await login("U08"), grp(5), ck, "E28")).quote.json.total, 4500, "ยอด"));
T("E29", "BR-06 แพ็กเกจ 4 คน ฿11,600", async (ck) => {
  const r = await (await login("U08")).post("/api/price", { type: "package", serviceCode: "P01", people: 4, date: "2026-10-16", time: "10:00" });
  ck.eq(r.json.total, 11600, "ยอด");
  ck.eq(r.json.discountAmount, 0, "ไม่มีส่วนลดกลุ่ม");
});

T("E30", "BR-07 ยกเลิกเหลือ 24:01 ชม.", async (ck) => ck.eq((await (await login("U01")).post("/api/bookings/5/cancel")).status, 200, "status"), { now: "2026-10-10T09:59:00+07:00" });
T("E31", "BR-07 ยกเลิกเหลือ 24:00 ชม. พอดี + รอบว่างทันที", async (ck) => {
  ck.eq((await (await login("U01")).post("/api/bookings/5/cancel")).status, 200, "status");
  const r = await slotsOf({ service: "S05", date: "2026-10-11", type: "single", people: 1 });
  const s = (r.json.slots ?? []).find((x) => x.time === "10:00");
  ck.ok(s?.therapists.some((x) => x.code === "T04"), "T04 รอบ 11 ต.ค. 10:00 ว่าง");
});
T("E32", "BR-07 ยกเลิกเหลือ 23:59 ชม.", async (ck) => {
  const c = await login("U01");
  const list = await c.get("/api/me/bookings");
  ck.eq(list.json.bookings.find((b) => b.code === "B05")?.canCancel, false, "ปุ่มกดไม่ได้");
  const r = await c.post("/api/bookings/5/cancel");
  ck.eq(r.status, 422, "status");
  ck.ok(typeof r.json.phone === "string", "มีเบอร์ร้าน");
}, { now: "2026-10-10T10:01:00+07:00" });
T("E33", "BR-07 ยกเลิกนัดวันนี้ B06", async (ck) => {
  const c = await login("U01");
  ck.eq((await c.get("/api/me/bookings")).json.bookings.find((b) => b.code === "B06")?.canCancel, false, "ปุ่มกดไม่ได้");
  ck.eq((await c.post("/api/bookings/6/cancel")).status, 422, "status");
});

T("E34", "BR-08 ตัวกรอง 4.5+", async (ck) => {
  const r = await guest().get("/api/therapists?min=4.5");
  ck.eq(r.json.therapists.map((x) => x.code), ["T01", "T02", "T05"], "รายชื่อ");
});
T("E35", "BR-08 การแสดงคะแนน", async (ck) => {
  const all = (await guest().get("/api/therapists")).json.therapists;
  const by = (c) => all.find((x) => x.code === c);
  ck.eq(by("T01").rating, "5.0", "T01");
  ck.eq(by("T03").rating, "4.4", "T03");
  ck.eq(by("T01").reviewCount, 3, "T01 รีวิว");
  ck.eq(by("T03").reviewCount, 5, "T03 รีวิว");
  ck.eq(by("T04").rating, null, "T04 ยังไม่มีรีวิว");
});
T("E36", "BR-08 ปัดทศนิยม (unit)", async (ck) => {
  ck.eq(R.formatRating(R.roundAverage(4.45)), "4.5", "4.45 แสดง");
  ck.eq(R.passesRatingFilter(R.roundAverage(4.45)), true, "4.45 ผ่าน");
  ck.eq(R.formatRating(R.roundAverage(4.44)), "4.4", "4.44 แสดง");
  ck.eq(R.passesRatingFilter(R.roundAverage(4.44)), false, "4.44 ไม่ผ่าน");
  ck.eq(R.formatRating(R.ratingTenths(89, 20)), "4.5", "89/20 = 4.45");
}, { unit: true });
T("E37", "BR-09 ฿99 / ฿100 / ฿199 (unit)", async (ck) => {
  ck.eq(R.pointsFor(9900), 0, "฿99");
  ck.eq(R.pointsFor(10000), 1, "฿100");
  ck.eq(R.pointsFor(19900), 1, "฿199");
}, { unit: true });
T("E38", "BR-09 ฿1,250 (unit)", async (ck) => ck.eq(R.pointsFor(125000), 12, "฿1,250"), { unit: true });
T("E39", "BR-09 B05 เสร็จ ได้ 7 แต้ม", async (ck) => {
  owner = await login("OWNER");
  const r = await owner.post("/api/admin/bookings/5/complete", {});
  ck.eq(r.json.pointsEarned, 7, "แต้มที่ได้");
  ck.eq((await (await login("U01")).get("/api/me")).json.points, 106, "แต้มรวม");
});
T("E40", "BR-09 ได้แต้มหลังร้านกดเสร็จ", async (ck) => {
  const u = await login("U01");
  ck.eq((await u.get("/api/me")).json.points, 99, "ก่อน");
  await (await login("OWNER")).post("/api/admin/bookings/B05/complete", {});
  ck.eq((await u.get("/api/me")).json.points, 106, "หลัง");
});

const s05 = (extra = {}) => ({ type: "single", serviceCode: "S05", date: "2026-10-20", time: "10:00", ...extra });
T("E41", "BR-10 แต้ม 99 แลกไม่ได้", async (ck) => {
  const u = await login("U01");
  ck.eq((await u.get("/api/me")).json.maxRedeemBlocks, 0, "แลกได้ 0 ครั้ง");
  ck.eq((await u.post("/api/price", s05({ redeemBlocks: 1 }))).status, 422, "แลก 1 ครั้ง");
});
T("E42", "BR-10 แต้ม 100 แลก 1 ครั้ง เหลือ 0", async (ck) => {
  const u = await login("U05");
  const r = await quoteAndBook(u, s05({ redeemBlocks: 1 }), ck, "E42");
  ck.eq(r.quote.json.pointsDiscount, 50, "ลด ฿50");
  ck.eq((await u.get("/api/me")).json.points, 0, "เหลือ 0");
});
T("E43", "BR-10 แต้ม 199 แลก 1 ครั้ง เหลือ 99", async (ck) => {
  const u = await login("U06");
  ck.eq((await u.get("/api/me")).json.maxRedeemBlocks, 1, "แลกได้ 1 ครั้ง");
  const r = await quoteAndBook(u, s05({ redeemBlocks: 1 }), ck, "E43");
  ck.eq(r.quote.json.pointsDiscount, 50, "ลด ฿50");
  ck.eq((await u.get("/api/me")).json.points, 99, "เหลือ 99");
});
T("E44", "BR-10 แต้ม 250 สูงสุด 2 ครั้ง เหลือ 50", async (ck) => {
  const u = await login("U04");
  ck.eq((await u.get("/api/me")).json.maxRedeemBlocks, 2, "แลกได้ 2 ครั้ง");
  ck.eq((await u.post("/api/price", s05({ redeemBlocks: 3 }))).status, 422, "แลก 3 ครั้งไม่ได้");
  const r = await quoteAndBook(u, s05({ redeemBlocks: 2 }), ck, "E44");
  ck.eq(r.quote.json.pointsDiscount, 100, "ลด ฿100");
  ck.eq((await u.get("/api/me")).json.points, 50, "เหลือ 50");
});
T("E45", "BR-10 ส่วนลดแต้มไม่ทำให้ติดลบ (unit)", async (ck) => {
  ck.eq(R.redeemPoints(2, 200, 8000).discount, 8000, "ลดได้ไม่เกิน ฿80");
  const p = R.calcPrice({ type: "single", unitPrice: 8000, people: 1, tierPct: 0, birthdayApplied: false, points: 200, redeemBlocks: 2, transport: null, giftCardBalance: null });
  ck.eq(p.price.total, 0, "ยอด ฿0");
}, { unit: true });

T("E46", "BR-11 ฿9,999 / ฿10,000 / ฿10,001", async (ck) => {
  ck.eq((await (await login("U04")).get("/api/me")).json.tier, "silver", "U04");
  ck.eq((await (await login("U07")).get("/api/me")).json.tier, "gold", "U07");
  ck.eq(R.tierOf(1000100), "gold", "฿10,001 (unit)");
});
T("E47", "BR-11 ฿29,999 / ฿30,000 / ฿30,001", async (ck) => {
  ck.eq((await (await login("U05")).get("/api/me")).json.tier, "gold", "U05");
  ck.eq((await (await login("U02")).get("/api/me")).json.tier, "platinum", "U02");
  ck.eq(R.tierOf(3000100), "platinum", "฿30,001 (unit)");
});
T("E48", "BR-11 Gold S04 ฿1,900", async (ck) => ck.eq((await quoteAndBook(await login("U01"), { type: "single", serviceCode: "S04", date: "2026-10-20", time: "10:00" }, ck, "E48")).quote.json.total, 1900, "ยอด"));
T("E49", "BR-11 Gold S05 ฿760", async (ck) => ck.eq((await quoteAndBook(await login("U01"), s05(), ck, "E49")).quote.json.total, 760, "ยอด"));
T("E50", "BR-11 Gold ฿1,250 → ฿1,187.50 (unit)", async (ck) => {
  const p = R.calcPrice({ type: "single", unitPrice: 125000, people: 1, tierPct: 5, birthdayApplied: false, points: 0, redeemBlocks: 0, transport: null, giftCardBalance: null }).price;
  ck.eq(p.discountAmount, 6250, "ส่วนลด ฿62.50");
  ck.eq(p.total, 118750, "ยอด ฿1,187.50");
  ck.eq(p.pointsToEarn, 11, "แต้ม 11");
}, { unit: true });
T("E51", "BR-12 ข้อความระดับ", async (ck) => {
  ck.eq((await (await login("U03")).get("/api/me")).json.tierMessage, "อีก ฿10,000 ถึง Gold", "U03");
  ck.eq((await (await login("U04")).get("/api/me")).json.tierMessage, "อีก ฿1 ถึง Gold", "U04");
  ck.eq((await (await login("U07")).get("/api/me")).json.tierMessage, "อีก ฿20,000 ถึง Platinum", "U07");
  ck.eq((await (await login("U01")).get("/api/me")).json.tierMessage, "อีก ฿17,600 ถึง Platinum", "U01");
});
T("E52", "BR-12 ข้อความระดับสูงสุด", async (ck) => {
  ck.eq((await (await login("U05")).get("/api/me")).json.tierMessage, "อีก ฿1 ถึง Platinum", "U05");
  ck.eq((await (await login("U02")).get("/api/me")).json.tierMessage, "อยู่ระดับสูงสุดแล้ว", "U02");
  const u6 = (await (await login("U06")).get("/api/me")).json.tierMessage;
  ck.eq(u6, "อยู่ระดับสูงสุดแล้ว", "U06");
  ck.ok(!String(u6).includes("-") && !String(u6).includes("15,000"), "U06 ไม่มี −฿15,000");
});

T("E53", "BR-13 วันนัดนอก/ในเดือนเกิด", async (ck) => {
  const el = (d) => R.birthdayEligible({ birthDate: "1992-10-15", apptDate: d, alreadyUsed: false, type: "single" });
  ck.eq(el("2026-09-30"), false, "30 ก.ย. (unit)");
  ck.eq(el("2026-10-01"), true, "1 ต.ค. (unit)");
  ck.eq(el("2026-10-31"), true, "31 ต.ค. (unit)");
  ck.eq(el("2026-11-01"), false, "1 พ.ย. (unit)");
  const u = await login("U02");
  ck.eq((await u.post("/api/price", { type: "single", serviceCode: "S01", date: "2026-10-31", time: "10:00" })).json.birthdayAvailable, true, "31 ต.ค. มีตัวเลือก");
  ck.eq((await u.post("/api/price", { type: "single", serviceCode: "S01", date: "2026-11-01", time: "10:00" })).json.birthdayAvailable, false, "1 พ.ย. ไม่มีตัวเลือก");
});
T("E54", "BR-13 Platinum เดือนเกิด ฿1,000 → ฿800", async (ck) => {
  const r = await quoteAndBook(await login("U02"), { type: "single", serviceCode: "S01", date: "2026-10-20", time: "10:00", useBirthday: true }, ck, "E54");
  ck.eq(r.quote.json.total, 800, "ยอด");
});
T("E55", "BR-13 เดือนเกิดครั้งที่ 2", async (ck) => {
  const u = await login("U05");
  const body = { type: "single", serviceCode: "S07", date: "2026-10-20", time: "10:00" };
  ck.eq((await u.post("/api/price", body)).json.birthdayAvailable, false, "ไม่มีตัวเลือก");
  ck.eq((await u.post("/api/price", { ...body, useBirthday: true })).status, 422, "ขอใช้แล้วถูกปฏิเสธ");
  ck.eq((await quoteAndBook(u, body, ck, "E55")).quote.json.total, 1710, "ยอด Gold 5%");
});
T("E56", "BR-13 จองคู่เดือนเกิด ฿2,240", async (ck) => {
  const r = await quoteAndBook(await login("U02"), { type: "couple", serviceCode: "S02", people: 2, date: "2026-10-24", time: "10:00", useBirthday: true }, ck, "E56");
  ck.eq(r.quote.json.total, 2240, "ยอด");
});
T("E57", "BR-13 แพ็กเกจในเดือนเกิด ฿2,900", async (ck) => {
  const u = await login("U02");
  const body = { type: "package", serviceCode: "P01", people: 1, date: "2026-10-20", time: "10:00" };
  const r = await u.post("/api/price", body);
  ck.eq(r.json.birthdayAvailable, false, "ไม่มีตัวเลือก");
  ck.eq(r.json.total, 2900, "ยอด");
});

const course = (date) => ({ type: "course", serviceCode: "K01", date, time: "10:00" });
T("E58", "BR-14 คอร์สเหลือ 0 / 1", async (ck) => {
  ck.eq((await (await login("U06")).post("/api/price", course("2026-10-19"))).status, 422, "U06 เหลือ 0");
  const r = await quoteAndBook(await login("U07"), course("2026-10-19"), ck, "E58");
  ck.eq(r.booking?.status, 201, "U07 เหลือ 1 จองได้");
  ck.eq(r.quote.json.total, 0, "ราคา ฿0");
});
T("E59", "BR-14 วันหมดอายุคอร์ส 19 / 20 / 21 ต.ค.", async (ck) => {
  const u = await login("U07");
  ck.eq((await u.post("/api/price", course("2026-10-19"))).status, 200, "19 ต.ค.");
  ck.eq((await u.post("/api/price", course("2026-10-20"))).status, 200, "20 ต.ค.");
  ck.eq((await u.post("/api/price", course("2026-10-21"))).status, 422, "21 ต.ค.");
  ck.eq((await book(u, course("2026-10-20"))).status, 201, "จองวันสุดท้าย");
});
T("E60", "BR-14 คอร์สหมดอายุแต่ยังเหลือครั้ง", async (ck) => {
  const u = await login("U05");
  ck.eq((await u.post("/api/price", course("2026-10-20"))).status, 422, "ใช้ไม่ได้");
  const c = (await u.get("/api/wallet")).json.courses.find((x) => x.code === "C04");
  ck.eq(c?.expired, true, "Wallet หมดอายุแล้ว");
  ck.eq(c?.remaining, 5, "เหลือ 5");
});
T("E61", "BR-14 ซื้อคอร์สใหม่วันนี้", async (ck) => {
  const u = await login("U03");
  const r = await u.post("/api/courses");
  ck.eq(r.status, 201, "status");
  ck.eq(r.json.price, 15000, "ราคา");
  ck.eq(r.json.total, 11, "11 ครั้ง");
  ck.eq(r.json.expiresOn, "2027-04-08", "หมดอายุ");
  const me = (await u.get("/api/me")).json;
  ck.eq(me.lifetimeSpend, 15000, "ยอดสะสม");
  ck.eq(me.tier, "gold", "ระดับ");
});
T("E62", "BR-14 Wallet คุณนิดา", async (ck) => {
  const c = (await (await login("U01")).get("/api/wallet")).json.courses.find((x) => x.code === "C01");
  ck.eq(c?.remainingLabel, "เหลือ 7 จาก 11 ครั้ง", "ข้อความ");
  ck.eq(c?.expiresOn, "2027-01-28", "หมดอายุ");
  ck.eq(c?.daysLeft, 110, "อีก 110 วัน");
});
T("E63", "BR-14 ยกเลิกนัดคอร์สไม่ตัดครั้ง", async (ck) => {
  const u = await login("U01");
  const b = await book(u, course("2026-10-20"));
  ck.eq(b.status, 201, "จอง");
  ck.eq((await u.get("/api/wallet")).json.courses.find((x) => x.code === "C01")?.remaining, 6, "หลังจองเหลือ 6");
  ck.eq((await u.post(`/api/bookings/${b.json.bookingId}/cancel`)).status, 200, "ยกเลิก");
  ck.eq((await u.get("/api/wallet")).json.courses.find((x) => x.code === "C01")?.remaining, 7, "หลังยกเลิกเหลือ 7");
});

const gc = (value) => ({ value, design: "lotus", channel: "line", recipient: "mom.fon" });
T("E64", "BR-15 ฿499 / ฿500", async (ck) => {
  const u = await login("U04");
  ck.eq((await u.post("/api/giftcards", gc(499))).status, 422, "฿499");
  ck.eq((await u.post("/api/giftcards", gc(500))).status, 201, "฿500");
});
T("E65", "BR-15 ฿10,000 / ฿10,001", async (ck) => {
  const u = await login("U04");
  ck.eq((await u.post("/api/giftcards", gc(10000))).status, 201, "฿10,000");
  ck.eq((await u.post("/api/giftcards", gc(10001))).status, 422, "฿10,001");
});
T("E66", "BR-15 ฿500.50", async (ck) => ck.eq((await (await login("U04")).post("/api/giftcards", gc(500.5))).status, 422, "status"));
T("E67", "BR-16 อายุบัตรซื้อวันนี้", async (ck) => {
  const r = await (await login("U04")).post("/api/giftcards", gc(1000));
  ck.eq(r.json.expiresOn, "2027-10-10", "หมดอายุ (API)");
  ck.eq(R.giftCardStatus("2027-10-09", "2027-10-10", 100000), "ok", "+364 (unit)");
  ck.eq(R.giftCardStatus("2027-10-10", "2027-10-10", 100000), "ok", "+365 (unit)");
  ck.eq(R.giftCardStatus("2027-10-11", "2027-10-10", 100000), "expired", "+366 (unit)");
});
T("E68", "BR-16 GC03 วันสุดท้าย / GC04 หมดอายุ", async (ck) => {
  const u = await login("U02");
  const base = { type: "single", serviceCode: "S01", date: "2026-10-20", time: "10:00" };
  const a = await u.post("/api/price", { ...base, giftCardCode: "SABAI-GC-LAST" });
  ck.eq(a.json.giftCardError, null, "GC03 ใช้ได้");
  ck.eq(a.json.giftcardPaid, 500, "GC03 หักยอด ฿500");
  const b = await u.post("/api/price", { ...base, giftCardCode: "SABAI-GC-EXP" });
  ck.eq(b.json.giftCardError?.message, MSG.GC_EXPIRED, "GC04 ข้อความ");
  ck.eq(b.json.giftcardPaid, 0, "GC04 ไม่หักยอด");
  await reset("2026-10-11T10:00:00+07:00");
  const c = await (await login("U02")).post("/api/price", { ...base, giftCardCode: "SABAI-GC-LAST" });
  ck.eq(c.json.giftCardError?.message, MSG.GC_EXPIRED, "GC03 เมื่อ TODAY = 11 ต.ค.");
});
T("E69", "BR-16 GC01 จ่าย ฿1,500 เหลือ ฿500", async (ck) => {
  const u = await login("U04");
  const r = await quoteAndBook(u, { type: "single", serviceCode: "S06", date: "2026-10-20", time: "10:00", giftCardCode: "SABAI-GC-2000" }, ck, "E69");
  ck.eq(r.quote.json.giftcardPaid, 1500, "ใช้บัตร");
  ck.eq(r.quote.json.giftCard?.balanceAfter, 500, "เหลือในหน้าสรุป");
  ck.eq((await u.get("/api/giftcards/SABAI-GC-2000")).json.balance, 500, "เหลือใน db");
});
T("E70", "BR-16 GC01 จ่าย ฿2,000 เหลือ ฿0", async (ck) => {
  const u = await login("U04");
  const r = await quoteAndBook(u, { type: "single", serviceCode: "S04", date: "2026-10-20", time: "10:00", giftCardCode: "SABAI-GC-2000" }, ck, "E70");
  ck.eq(r.quote.json.giftcardPaid, 2000, "ใช้บัตร");
  ck.eq(r.quote.json.otherPaid, 0, "จ่ายเพิ่ม");
  ck.eq((await u.get("/api/giftcards/SABAI-GC-2000")).json.balance, 0, "เหลือใน db");
});
T("E71", "BR-16 ยอด ฿2,500 บัตร ฿2,000 (unit)", async (ck) => {
  const p = R.calcPrice({ type: "single", unitPrice: 250000, people: 1, tierPct: 0, birthdayApplied: false, points: 0, redeemBlocks: 0, transport: null, giftCardBalance: 200000 }).price;
  ck.eq(p.giftcardPaid, 200000, "ใช้บัตร ฿2,000");
  ck.eq(p.otherPaid, 50000, "จ่ายเพิ่ม ฿500");
}, { unit: true });
T("E72", "BR-16 บัตรยอด ฿0", async (ck) => {
  const r = await (await login("U04")).post("/api/price", { type: "single", serviceCode: "S01", date: "2026-10-20", time: "10:00", giftCardCode: "SABAI-GC-ZERO" });
  ck.eq(r.json.giftcardPaid, 0, "หักไม่ได้");
  ck.eq(r.json.otherPaid, r.json.total, "จ่ายช่องทางอื่นเต็มจำนวน");
  ck.eq(r.json.total, 1000, "ยอดเต็ม");
});

const tr = (q) => guest().get(`/api/transport?${new URLSearchParams(q)}`);
T("E73", "BR-17 5.0 กม. ฟรี", async (ck) => {
  ck.eq((await tr({ hotel: "H02", people: 1 })).json.fee, 0, "ค่ารถ");
  ck.eq((await guest().post("/api/price", { type: "single", serviceCode: "S01", date: "2026-10-20", time: "10:00", hotelCode: "H02" })).json.transportFee, 0, "ในใบสรุป");
});
T("E74", "BR-17 5.1 กม. ฿300", async (ck) => ck.eq((await tr({ hotel: "H03", people: 1 })).json.fee, 300, "ค่ารถ"));
T("E75", "BR-17 12 กม. ฿300", async (ck) => ck.eq((await tr({ hotel: "H04", people: 1 })).json.fee, 300, "ค่ารถ"));
T("E76", "BR-17 15.0 กม. ฿300", async (ck) => {
  ck.eq((await tr({ hotel: "H05", people: 1 })).json.fee, 300, "ค่ารถ");
  ck.eq((await tr({ distance: "15.0", people: 1 })).json.fee, 300, "พิมพ์ 15.0 เอง");
});
T("E77", "BR-17 15.1 กม. นอกพื้นที่", async (ck) => {
  const r = await tr({ hotel: "H06", people: 1 });
  ck.eq(r.status, 422, "status");
  ck.eq(r.json.message, MSG.OUT_OF_AREA, "ข้อความ");
  ck.eq((await tr({ distance: "15.1", people: 1 })).json.message, MSG.OUT_OF_AREA, "พิมพ์ 15.1 เอง");
  const p = await guest().post("/api/price", { type: "single", serviceCode: "S01", date: "2026-10-20", time: "10:00", hotelCode: "H06" });
  ck.eq(p.json.message, MSG.OUT_OF_AREA, "ในใบสรุป");
});
T("E78", "BR-18 3 / 4 / 5 คน 12 กม.", async (ck) => {
  const a = (await tr({ hotel: "H04", people: 3 })).json;
  const b = (await tr({ hotel: "H04", people: 4 })).json;
  const c = (await tr({ hotel: "H04", people: 5 })).json;
  ck.eq([a.vehicles, a.fee], [1, 300], "3 คน");
  ck.eq([b.vehicles, b.fee], [1, 300], "4 คน");
  ck.eq([c.vehicles, c.fee], [2, 600], "5 คน");
  const p = await (await login("U08")).post("/api/price", grp(5, { hotelCode: "H04" }));
  ck.eq([p.json.vehicles, p.json.transportFee], [2, 600], "ใบสรุปกลุ่ม 5 คน");
});
T("E79", "BR-18 6 คน 12 กม. ฿6,000", async (ck) => {
  const r = await quoteAndBook(await login("U08"), grp(6, { hotelCode: "H04" }), ck, "E79");
  ck.eq(r.quote.json.transportFee, 600, "ค่ารถ 2 คัน");
  ck.eq(r.quote.json.total, 6000, "ยอด");
});
T("E80", "BR-18 5 คน 5.0 กม.", async (ck) => {
  const r = (await tr({ hotel: "H02", people: 5 })).json;
  ck.eq([r.vehicles, r.fee], [2, 0], "2 คัน ฿0");
});
T("E81", "BR-19 Bangkok Relax 1 / 2 / 4 คน", async (ck) => {
  const u = await login("U08");
  const pk = (n) => ({ type: "package", serviceCode: "P01", people: n, date: "2026-10-16", time: "10:00" });
  ck.eq((await u.post("/api/price", pk(1))).json.total, 2900, "1 คน");
  ck.eq((await quoteAndBook(u, pk(2), ck, "E81")).quote.json.total, 5800, "2 คน");
  ck.eq((await u.post("/api/price", pk(4))).json.total, 11600, "4 คน");
});
T("E82", "BR-19 2 คน 12 กม. รถรวมแล้ว", async (ck) => {
  const r = await quoteAndBook(await login("U08"), { type: "package", serviceCode: "P01", people: 2, date: "2026-10-16", time: "10:00", hotelCode: "H04" }, ck, "E82");
  ck.eq(r.quote.json.transportFee, 0, "ค่ารถ");
  ck.eq(r.quote.json.total, 5800, "ยอด");
});
T("E83", "BR-19 15.1 กม.", async (ck) => {
  const r = await (await login("U08")).post("/api/price", { type: "package", serviceCode: "P01", people: 2, date: "2026-10-16", time: "10:00", hotelCode: "H06" });
  ck.eq(r.status, 422, "status");
  ck.eq(r.json.message, MSG.OUT_OF_AREA, "ข้อความ");
});
T("E84", "BR-20 กลุ่ม 4 + Gold ฿3,600", async (ck) => ck.eq((await quoteAndBook(await login("U01"), grp(4), ck, "E84")).quote.json.total, 3600, "ยอด"));
T("E85", "BR-20 กลุ่ม 4 + Platinum ฿3,600", async (ck) => ck.eq((await quoteAndBook(await login("U02"), grp(4, { date: "2026-11-02" }), ck, "E85")).quote.json.total, 3600, "ยอด"));
T("E86", "BR-20 กลุ่ม 4 + เดือนเกิด ฿3,200", async (ck) => ck.eq((await quoteAndBook(await login("U02"), grp(4, { date: "2026-10-31", useBirthday: true }), ck, "E86")).quote.json.total, 3200, "ยอด"));
T("E87", "BR-20 กลุ่ม 4 + แต้ม 200 + รถ 12 กม. ฿3,800", async (ck) => {
  const u = await login("U04");
  const r = await quoteAndBook(u, grp(4, { redeemBlocks: 2, hotelCode: "H04" }), ck, "E87");
  ck.eq(r.quote.json.total, 3800, "ยอด");
  ck.eq((await u.get("/api/me")).json.points, 50, "แต้มเหลือ");
});
T("E88", "BR-20 E87 + GC01", async (ck) => {
  const u = await login("U04");
  const r = await quoteAndBook(u, grp(4, { redeemBlocks: 2, hotelCode: "H04", giftCardCode: "SABAI-GC-2000" }), ck, "E88");
  ck.eq(r.quote.json.total, 3800, "ยอดสุทธิ");
  ck.eq(r.quote.json.giftcardPaid, 2000, "ใช้บัตร");
  ck.eq(r.quote.json.otherPaid, 1800, "จ่ายเพิ่ม");
  ck.eq(r.quote.json.pointsToEarn, 15, "แต้มที่จะได้");
  ck.eq((await u.get("/api/giftcards/SABAI-GC-2000")).json.balance, 0, "บัตรเหลือ");
  if (r.booking?.status === 201) {
    const done = await (await login("OWNER")).post(`/api/admin/bookings/${r.booking.json.bookingId}/complete`, {});
    ck.eq(done.json.pointsEarned, 15, "แต้มที่ได้จริงหลังเสร็จ");
  }
});
T("E89", "BR-20 Platinum + แลกแต้ม ฿670", async (ck) => {
  const u = await login("U06");
  const r = await quoteAndBook(u, s05({ redeemBlocks: 1 }), ck, "E89");
  ck.eq(r.quote.json.total, 670, "ยอด");
  ck.eq((await u.get("/api/me")).json.points, 99, "แต้มเหลือ");
});
T("E90", "BR-20 / NFR-17 ยอดหน้าสรุป = ยอดที่บันทึก (ทุกการจองใน E26–E89)", async (ck) => {
  ck.ok(e90.checked >= 15, `ต้องตรวจอย่างน้อย 15 การจอง (ตรวจได้ ${e90.checked})`);
  for (const m of e90.mismatches) ck.ok(false, m);
}, { unit: true, last: true });

// ── รัน ────────────────────────────────────────────────────────────────────
async function main() {
  const health = await fetch(`${BASE}/api/health`).then((r) => r.json()).catch(() => null);
  if (!health?.db) {
    console.error(`เชื่อมต่อ ${BASE}/api/health ไม่ได้ หรือ db=false`);
    process.exit(2);
  }
  R = await import("../lib/rules/index.ts");

  console.log(`ตรวจกฎร้าน ${BASE} · ${cases.length} เคส\n`);
  const failed = [];
  let passed = 0;
  for (const c of cases) {
    const ck = new Check();
    try {
      if (!c.unit) await reset(c.now);
      owner = null;
      await c.fn(ck);
    } catch (e) {
      ck.fails.push(`exception: ${e.message}`);
    }
    if (ck.fails.length === 0) {
      passed++;
      console.log(`✅ ${c.id} ${c.title}`);
    } else {
      failed.push({ id: c.id, title: c.title, fails: ck.fails });
      console.log(`❌ ${c.id} ${c.title}\n   - ${ck.fails.join("\n   - ")}`);
    }
  }
  await reset();
  console.log(`\nผ่าน ${passed} / ${cases.length} ข้อ`);
  if (failed.length) {
    console.log("รายการที่ล้ม: " + failed.map((f) => f.id).join(", "));
    process.exit(1);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(2);
});
