// CR-04 วันหยุดร้าน (ส่วน ก: 23 ต.ค. · 5 ธ.ค. · 31 ธ.ค. 2569 ปิดทุกช่องทาง)
//   ใช้ (PowerShell จากโฟลเดอร์บท): node tests/cr04.mjs          (ค่าเริ่ม BASE_URL=http://localhost:4000)
//   ต้องเปิด ALLOW_TEST_RESET=1 · reset ก่อนทุกเคส (วันนี้ = 10 ต.ค. 2026 10:00 เว้นแต่เคสระบุ)
//   ค่าที่คาดหวังจาก docs/impact/CR-04.md §5 · ป้าย [D:CR-04] = CR + คำตอบร้าน · [E] = ล็อกพฤติกรรมเดิม
//   ข้อความไทย/จีนส่งผ่าน node (ไม่ผ่าน PowerShell) · Node >= 22 · ไม่มี dependency

const BASE = (process.env.BASE_URL || "http://localhost:4000").replace(/\/$/, "");
const TODAY = "2026-10-10T10:00:00+07:00";
const USERS = { U01: ["nida@sabai.test", "Nida@2026"], OWNER: ["owner@sabai.test", "Owner@2026"] };
const HOLIDAYS = [
  { date: "2026-10-23", th: "วันปิยมหาราช", en: "Chulalongkorn Day", zh: "五世王纪念日" },
  { date: "2026-12-05", th: "วันพ่อแห่งชาติ", en: "National Father's Day", zh: "父亲节" },
  { date: "2026-12-31", th: "วันสิ้นปี", en: "New Year's Eve", zh: "新年前夕" },
];
const MSG = {
  th: (n) => `วันนี้ร้านหยุด (${n}) กรุณาเลือกวันอื่น`,
  en: (n) => `The shop is closed on this day (${n}). Please choose another date`,
  zh: (n) => `本店当天休息（${n}），请选择其他日期`,
};

class Client {
  constructor(lang) {
    this.cookie = "";
    this.lang = lang;
  }
  async req(method, path, body) {
    const headers = { "Content-Type": "application/json" };
    const ck = [this.cookie, this.lang ? `lang=${this.lang}` : ""].filter(Boolean).join("; ");
    if (ck) headers.Cookie = ck;
    const r = await fetch(BASE + path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
    const m = (r.headers.get("set-cookie") || "").match(/sabai_session=([^;]*)/);
    if (m) this.cookie = `sabai_session=${m[1]}`;
    const text = await r.text();
    let json;
    try {
      json = JSON.parse(text);
    } catch {
      json = { raw: text.slice(0, 120) };
    }
    return { status: r.status, json };
  }
  post(p, b = {}) {
    return this.req("POST", p, b);
  }
  get(p) {
    return this.req("GET", p);
  }
}
async function login(u) {
  const c = new Client();
  const [email, password] = USERS[u];
  const r = await c.post("/api/auth/login", { email, password });
  if (r.status !== 200) throw new Error(`login ${u}: ${r.status}`);
  return c;
}
async function reset(now = TODAY) {
  const r = await new Client().post("/api/test/reset", { now });
  if (r.status !== 200) throw new Error(`reset: ${r.status} ${JSON.stringify(r.json)}`);
}
const slots = (c, date, service = "S01", type = "single", people = 1) =>
  c.get(`/api/slots?${new URLSearchParams({ service, date, type, people: String(people) })}`);
async function queue(date) {
  const o = await login("OWNER");
  const r = await o.get(`/api/admin/bookings?date=${date}`);
  return (r.json.bookings ?? []).filter((b) => b.status !== "cancelled");
}
const guest = (o) => ({ type: "single", serviceCode: "S01", people: 1, date: "2026-10-23", time: "10:00", contactName: "คุณทดสอบ", contactPhone: "0899990004", ...o });

// ── ตัวตรวจ ──
const results = [];
function T(id, name, src, fn) {
  results.push({ id, name, src, fn });
}
class Ck {
  constructor() {
    this.fails = [];
  }
  eq(a, b, what) {
    const A = JSON.stringify(a);
    const B = JSON.stringify(b);
    if (A !== B) this.fails.push(`${what}: ได้ ${A} คาด ${B}`);
  }
  ok(v, what) {
    if (!v) this.fails.push(what);
  }
}
const closed = (ck, r, name, lang = "th", what = "") => {
  ck.eq(r.status, 422, `${what}status`);
  ck.eq(r.json.error, "SHOP_CLOSED", `${what}error`);
  if (name) ck.eq(r.json.message, MSG[lang](name), `${what}message`);
};

T("H1", "GET /api/holidays → 200 · 3 แถวเรียงวันที่ · ชื่อ 3 ภาษาตรงตัว", "[D:CR-04] ②", async (ck) => {
  const r = await new Client("th").get("/api/holidays");
  ck.eq(r.status, 200, "status");
  const rows = r.json.holidays ?? [];
  ck.eq(rows.map((h) => h.date), HOLIDAYS.map((h) => h.date), "วันที่เรียง");
  ck.eq(rows.map((h) => [h.nameTh, h.nameEn, h.nameZh]), HOLIDAYS.map((h) => [h.th, h.en, h.zh]), "ชื่อ th/en/zh");
});
T("H2", "slots S01 23 ต.ค. (th) → 422 SHOP_CLOSED วันปิยมหาราช", "[D:CR-04] ③1 ②", async (ck) => {
  closed(ck, await slots(new Client("th"), "2026-10-23"), "วันปิยมหาราช", "th");
});
T("H3", "slots 23 ต.ค. cookie en / zh → ข้อความ en / zh", "[D:CR-04] ②", async (ck) => {
  closed(ck, await slots(new Client("en"), "2026-10-23"), "Chulalongkorn Day", "en", "en ");
  closed(ck, await slots(new Client("zh"), "2026-10-23"), "五世王纪念日", "zh", "zh ");
});
T("H4", "slots S01 22 ต.ค. และ 24 ต.ค. → 200 · 23 รอบ ว่าง 23 (เหมือนก่อนแก้)", "[D:CR-04] ③2 [E]", async (ck) => {
  for (const d of ["2026-10-22", "2026-10-24"]) {
    const r = await slots(new Client(), d);
    ck.eq(r.status, 200, `${d} status`);
    ck.eq([r.json.slots?.length, r.json.slots?.filter((s) => s.available).length], [23, 23], `${d} รอบ/ว่าง`);
  }
});
T("H5", "price guest single S01 23 ต.ค. 10:00 → 422 SHOP_CLOSED", "[D:CR-04] ②", async (ck) => {
  closed(ck, await new Client().post("/api/price", guest()), "วันปิยมหาราช");
});
T("H6", "bookings guest single 23 ต.ค. → 422 SHOP_CLOSED · คิว 23 ต.ค. ยังว่าง", "[D:CR-04] ②", async (ck) => {
  closed(ck, await new Client().post("/api/bookings", { ...guest(), quotedTotal: 1000 }), "วันปิยมหาราช");
  ck.eq((await queue("2026-10-23")).length, 0, "คิว 23 ต.ค.");
});
T("H7", "price couple / group / package P01 23 ต.ค. → 422 SHOP_CLOSED ทั้ง 3", "[D:CR-04] ② ทุกแบบ", async (ck) => {
  const c = new Client();
  closed(ck, await c.post("/api/price", guest({ type: "couple", people: 2 })), "วันปิยมหาราช", "th", "couple ");
  closed(ck, await c.post("/api/price", guest({ type: "group", people: 3 })), "วันปิยมหาราช", "th", "group ");
  closed(ck, await c.post("/api/price", guest({ type: "package", serviceCode: "P01", people: 1 })), "วันปิยมหาราช", "th", "package ");
});
T("H8", "U01 จองคอร์ส K01 (C01) 23 ต.ค. → 422 SHOP_CLOSED · คิวว่าง", "[D:CR-04] CR (จองด้วยคอร์ส) ②", async (ck) => {
  const c = await login("U01");
  const b = { type: "course", serviceCode: "K01", people: 1, date: "2026-10-23", time: "10:00" };
  closed(ck, await c.post("/api/price", b), "วันปิยมหาราช", "th", "price ");
  closed(ck, await c.post("/api/bookings", { ...b, quotedTotal: 0 }), "วันปิยมหาราช", "th", "bookings ");
  ck.eq((await queue("2026-10-23")).length, 0, "คิว 23 ต.ค.");
});
T("H9", "5 ธ.ค. ตอนนี้ (เกิน 30 วัน) → DATE_OUT_OF_RANGE ไม่ใช่ SHOP_CLOSED", "[D:CR-04] ③3 ① ข้อ 3", async (ck) => {
  const c = new Client();
  const s = await slots(c, "2026-12-05");
  ck.eq([s.status, s.json.error], [422, "DATE_OUT_OF_RANGE"], "slots");
  const p = await c.post("/api/price", guest({ date: "2026-12-05" }));
  ck.eq([p.status, p.json.error], [422, "DATE_OUT_OF_RANGE"], "price");
});
T("H10", "วันนี้ 10 พ.ย. → slots 5 ธ.ค. → SHOP_CLOSED วันพ่อแห่งชาติ", "[D:CR-04] ① ข้อ 3 ②", async (ck) => {
  await reset("2026-11-10T10:00:00+07:00");
  closed(ck, await slots(new Client(), "2026-12-05"), "วันพ่อแห่งชาติ");
});
T("H11", "วันนี้ 1 ธ.ค. → slots 31 ธ.ค. (+30) → SHOP_CLOSED วันสิ้นปี", "[D:CR-04] ① ②", async (ck) => {
  await reset("2026-12-01T10:00:00+07:00");
  closed(ck, await slots(new Client(), "2026-12-31"), "วันสิ้นปี");
});

async function chatFlow(lang, msgs) {
  const c = new Client();
  let state = null;
  let last = null;
  for (const m of msgs) {
    last = await c.post("/api/chat", { message: m, state, lang });
    if (last.status !== 200) return last;
    state = last.json.state;
  }
  return last;
}
T("H12", "แชท th: จองนวดไทย 60 → 2026-10-23 → ตอบร้านหยุด · ยังรอวันใหม่ · ไม่มีนัด", "[D:CR-04] CR (แชท) ②", async (ck) => {
  const r = await chatFlow("th", ["จองนวดไทย 60", "2026-10-23"]);
  ck.eq(r.status, 200, "status");
  ck.ok(String(r.json.reply ?? "").startsWith(MSG.th("วันปิยมหาราช")), `คำตอบแชทขึ้นต้นด้วยข้อความร้านหยุด (ได้ ${JSON.stringify(r.json.reply ?? r.json)})`);
  ck.eq(r.json.state?.step, "date", "state.step");
  ck.eq(r.json.booking ?? null, null, "ไม่มี booking");
});
T("H13", "แชท zh: 预约泰式按摩 60 → 2026-10-23 → ข้อความจีน", "[D:CR-04] ②", async (ck) => {
  const r = await chatFlow("zh", ["预约泰式按摩 60", "2026-10-23"]);
  ck.eq(r.status, 200, "status");
  ck.ok(String(r.json.reply ?? "").startsWith(MSG.zh("五世王纪念日")), `คำตอบแชทจีน (ได้ ${JSON.stringify(r.json.reply ?? r.json)})`);
});
T("H14", "จอง guest S01 22 ต.ค. 10:00 → 201 (ไม่ปิดเกิน)", "[D:CR-04] ③2", async (ck) => {
  const c = new Client();
  const b = guest({ date: "2026-10-22" });
  const q = await c.post("/api/price", b);
  ck.eq(q.status, 200, "price");
  const r = await c.post("/api/bookings", { ...b, quotedTotal: q.json.total });
  ck.eq(r.status, 201, "bookings");
});

// ── รัน ──
let pass = 0;
const failed = [];
const t0 = Date.now();
for (const t of results) {
  await reset();
  const ck = new Ck();
  try {
    await t.fn(ck);
  } catch (e) {
    ck.fails.push(`exception: ${e.message}`);
  }
  if (ck.fails.length) {
    failed.push(t.id);
    console.log(`✗ ${t.id} ${t.name}  ${t.src}`);
    for (const f of ck.fails) console.log(`    - ${f}`);
  } else {
    pass++;
    console.log(`✓ ${t.id} ${t.name}  ${t.src}`);
  }
}
await reset();
console.log(`\nCR-04: ผ่าน ${pass}/${results.length}${failed.length ? ` · ล้ม ${failed.join(" ")}` : ""} · ${((Date.now() - t0) / 1000).toFixed(1)} วิ`);
process.exit(failed.length ? 1 : 0);
