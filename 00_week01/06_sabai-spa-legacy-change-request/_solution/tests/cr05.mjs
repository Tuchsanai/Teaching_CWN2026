// CR-05 รายงานยอดสำหรับเจ้าของร้าน + CSV
//   ใช้ (PowerShell จากโฟลเดอร์บท): node tests/cr05.mjs [R1 R7 ...]   (ค่าเริ่ม BASE_URL=http://localhost:4000)
//   ต้องเปิด ALLOW_TEST_RESET=1 · reset ก่อนทุกเคส (วันนี้ = 10 ต.ค. 2026 10:00 เว้นแต่เคสระบุ)
//   ค่าที่คาดหวังมาจาก SQL ตรงกับฐาน (docs/impact/CR-05.md §3) ไม่ได้มาจากหน้ารายงาน
//   ป้าย [D:CR-05] = CR + คำตอบร้าน · [E sql:<คิวรี>] = ผล SQL หลัง reset
//   ข้อความไทยตรวจด้วย node (ไม่ผ่าน PowerShell) · Node >= 22 · ไม่มี dependency

const BASE = (process.env.BASE_URL || "http://localhost:4000").replace(/\/$/, "");
const TODAY = "2026-10-10T10:00:00+07:00";
const USERS = { U01: ["nida@sabai.test", "Nida@2026"], OWNER: ["owner@sabai.test", "Owner@2026"] };

const T6 = ["T01", "T02", "T03", "T04", "T05", "T06"];
const byT = (m) => T6.map((code) => ({ code, completed: m[code] ?? 0 }));
// [E sql:q_counts q_money q_pending q_therapist] · นิยาม [D:CR-05] ① ②
const EXP = {
  sep: {
    counts: { confirmed: 0, completed: 3, cancelled: 1 },
    revenue: 1900, giftcardPaid: 0, otherPaid: 1900, transportFee: 0,
    discounts: { group: 0, tier: 100, birthday: 0 },
    pointsEarned: 19, courseSessions: 2, pendingValue: 0,
    byTherapist: byT({ T01: 1, T03: 1, T05: 1 }),
  },
  oct: {
    counts: { confirmed: 6, completed: 1, cancelled: 0 },
    revenue: 1440, giftcardPaid: 0, otherPaid: 1440, transportFee: 0,
    discounts: { group: 0, tier: 0, birthday: 360 },
    pointsEarned: 14, courseSessions: 0, pendingValue: 11130,
    byTherapist: byT({ T05: 1 }),
  },
  zero: {
    counts: { confirmed: 0, completed: 0, cancelled: 0 },
    revenue: 0, giftcardPaid: 0, otherPaid: 0, transportFee: 0,
    discounts: { group: 0, tier: 0, birthday: 0 },
    pointsEarned: 0, courseSessions: 0, pendingValue: 0,
    byTherapist: byT({}),
  },
};
const FIELDS = Object.keys(EXP.sep);
const CSV_HEAD = "date,code,status,type,people,service,total,giftcard_paid,other_paid,discount_kind,discount_amount,points_earned";
// [E sql:q_csv_sep]
const CSV_SEP = [
  "2026-09-02,B10,completed,course,1,คอร์สกระชับสัดส่วน 10 แถม 1,0.00,0.00,0.00,none,0.00,0",
  "2026-09-16,B11,cancelled,course,1,คอร์สกระชับสัดส่วน 10 แถม 1,0.00,0.00,0.00,none,0.00,0",
  "2026-09-23,B12,completed,course,1,คอร์สกระชับสัดส่วน 10 แถม 1,0.00,0.00,0.00,none,0.00,0",
  "2026-09-30,B13,completed,single,1,นวดน้ำมันอโรมา,1900.00,0.00,1900.00,tier,100.00,19",
];
const RANGE_MSG = {
  th: "เลือกช่วงวันได้ไม่เกิน 92 วัน และวันเริ่มต้องไม่เกินวันสิ้นสุด",
  en: "Choose a range of at most 92 days, with the start date not after the end date",
  zh: "日期范围最多92天，且开始日期不能晚于结束日期",
};

class Client {
  constructor(lang) {
    this.cookie = "";
    this.lang = lang;
  }
  async raw(method, path, body) {
    const headers = { "Content-Type": "application/json" };
    const ck = [this.cookie, this.lang ? `lang=${this.lang}` : ""].filter(Boolean).join("; ");
    if (ck) headers.Cookie = ck;
    const r = await fetch(BASE + path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
    const m = (r.headers.get("set-cookie") || "").match(/sabai_session=([^;]*)/);
    if (m) this.cookie = `sabai_session=${m[1]}`;
    return r;
  }
  async req(method, path, body) {
    const r = await this.raw(method, path, body);
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
async function login(u, lang) {
  const c = new Client(lang);
  const [email, password] = USERS[u];
  const r = await c.post("/api/auth/login", { email, password });
  if (r.status !== 200) throw new Error(`login ${u}: ${r.status}`);
  return c;
}
async function reset(now = TODAY) {
  const r = await new Client().post("/api/test/reset", { now });
  if (r.status !== 200) throw new Error(`reset: ${r.status} ${JSON.stringify(r.json)}`);
}
const report = (c, from, to) => c.get(`/api/admin/report?${new URLSearchParams({ from, to })}`);
async function csv(c, from, to) {
  const r = await c.raw("GET", `/api/admin/report?${new URLSearchParams({ from, to, format: "csv" })}`);
  const bytes = new Uint8Array(await r.arrayBuffer());
  return { status: r.status, type: r.headers.get("content-type") || "", disp: r.headers.get("content-disposition") || "", bytes };
}
const addDays = (d, n) => new Date(Date.parse(`${d}T00:00:00Z`) + n * 86400000).toISOString().slice(0, 10);

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
function same(ck, r, exp, what = "") {
  ck.eq(r.status, 200, `${what}status`);
  for (const f of FIELDS) ck.eq(r.json[f], exp[f], `${what}${f}`);
}
const rangeErr = (ck, r, lang = "th", what = "") => {
  ck.eq(r.status, 422, `${what}status`);
  ck.eq(r.json.error, "REPORT_RANGE", `${what}error`);
  ck.eq(r.json.message, RANGE_MSG[lang], `${what}message`);
};

T("R1", "owner 1–30 ก.ย. → ทุกตัวเลขตาม SQL", "[D:CR-05] ①② [E sql:q_counts q_money q_pending q_therapist]", async (ck) => {
  same(ck, await report(await login("OWNER"), "2026-09-01", "2026-09-30"), EXP.sep);
});
T("R2", "owner 1–31 ต.ค. → ทุกตัวเลขตาม SQL", "[D:CR-05] ①② [E sql:q_counts q_money q_pending q_therapist]", async (ck) => {
  same(ck, await report(await login("OWNER"), "2026-10-01", "2026-10-31"), EXP.oct);
});
T("R3", "owner 6–9 ต.ค. → 200 ทุกค่า 0 (ไม่ใช่ error)", "[D:CR-05] ③1 [E sql:*]", async (ck) => {
  same(ck, await report(await login("OWNER"), "2026-10-06", "2026-10-09"), EXP.zero);
});
T("R4", "1 ส.ค.–31 ต.ค. (92 วัน) ดูได้ · 1 ส.ค.–1 พ.ย. (93 วัน) → 422", "[D:CR-05] ③2 [E sql:q_days q_counts q_money]", async (ck) => {
  const o = await login("OWNER");
  const r = await report(o, "2026-08-01", "2026-10-31");
  ck.eq(r.status, 200, "92 วัน status");
  ck.eq(r.json.counts, { confirmed: 6, completed: 6, cancelled: 1 }, "92 วัน counts");
  ck.eq([r.json.revenue, r.json.pointsEarned, r.json.courseSessions, r.json.pendingValue], [3340, 33, 4, 11130], "92 วัน revenue/points/course/pending");
  rangeErr(ck, await report(o, "2026-08-01", "2026-11-01"), "th", "93 วัน ");
});
T("R5", "from > to → 422 · วันที่ผิดรูป / ไม่ส่ง → 422", "[D:CR-05] ① ②", async (ck) => {
  const o = await login("OWNER");
  rangeErr(ck, await report(o, "2026-09-30", "2026-09-01"), "th", "from>to ");
  const same1 = await report(o, "2026-09-30", "2026-09-30");
  ck.eq(same1.status, 200, "from = to");
  const bad = await report(o, "2026-9-1", "2026-09-30");
  ck.eq(bad.status, 422, "ผิดรูป status");
  const none = await o.get("/api/admin/report");
  ck.eq(none.status, 422, "ไม่ส่งช่วง status");
});
T("R6", "สิทธิ์: ไม่ล็อกอิน 401 · สมาชิก U01 403 (JSON และ CSV)", "[D:CR-05] ② สิทธิ์ · CR \"เฉพาะเจ้าของร้าน\"", async (ck) => {
  const g = new Client();
  ck.eq((await report(g, "2026-09-01", "2026-09-30")).status, 401, "guest JSON");
  ck.eq((await csv(g, "2026-09-01", "2026-09-30")).status, 401, "guest CSV");
  const u = await login("U01");
  const r = await report(u, "2026-09-01", "2026-09-30");
  ck.eq([r.status, r.json.error], [403, "FORBIDDEN"], "U01 JSON");
  ck.ok(r.json.revenue === undefined, "U01 ไม่เห็นตัวเลข");
  ck.eq((await csv(u, "2026-09-01", "2026-09-30")).status, 403, "U01 CSV");
});
T("R7", "CSV ก.ย.: BOM · text/csv utf-8 · หัวคอลัมน์ · 4 แถวเรียงเวลา · ไทยตรงตัว", "[D:CR-05] ①② CR \"Excel อ่านไทยออก\" [E sql:q_csv_sep]", async (ck) => {
  const r = await csv(await login("OWNER"), "2026-09-01", "2026-09-30");
  ck.eq(r.status, 200, "status");
  ck.ok(/^text\/csv;\s*charset=utf-8$/i.test(r.type), `content-type (ได้ ${r.type})`);
  ck.ok(/attachment/i.test(r.disp), `content-disposition attachment (ได้ ${r.disp})`);
  ck.eq([...r.bytes.slice(0, 3)], [0xef, 0xbb, 0xbf], "3 ไบต์แรก (BOM)");
  const text = new TextDecoder("utf-8", { ignoreBOM: true }).decode(r.bytes.slice(3));
  const lines = text.split(/\r?\n/).filter((l) => l !== "");
  ck.eq(lines[0], CSV_HEAD, "หัวคอลัมน์");
  ck.eq(lines.length - 1, 4, "จำนวนแถวข้อมูล");
  ck.eq(lines.slice(1), CSV_SEP, "แถวข้อมูล");
});
T("R8", "CSV 6–9 ต.ค. → หัวคอลัมน์อย่างเดียว · CSV 93 วัน → 422", "[D:CR-05] ③1 ③2", async (ck) => {
  const o = await login("OWNER");
  const r = await csv(o, "2026-10-06", "2026-10-09");
  ck.eq(r.status, 200, "status");
  ck.eq([...r.bytes.slice(0, 3)], [0xef, 0xbb, 0xbf], "BOM");
  const lines = new TextDecoder().decode(r.bytes.slice(3)).split(/\r?\n/).filter((l) => l !== "");
  ck.eq(lines, [CSV_HEAD], "มีแต่หัวคอลัมน์");
  ck.eq((await csv(o, "2026-08-01", "2026-11-01")).status, 422, "CSV 93 วัน");
});
T("R9", "ขอบโซนเวลา: 30–30 ก.ย. = B13 18:00 · 1–5 ต.ค. = B07", "[D:CR-05] ① วันนัดเวลาไทย [E sql:q_csv_sep]", async (ck) => {
  const o = await login("OWNER");
  const a = await report(o, "2026-09-30", "2026-09-30");
  ck.eq([a.status, a.json.counts, a.json.revenue], [200, { confirmed: 0, completed: 1, cancelled: 0 }, 1900], "30 ก.ย.");
  const b = await report(o, "2026-10-01", "2026-10-05");
  ck.eq([b.status, b.json.counts, b.json.revenue, b.json.discounts], [200, { confirmed: 0, completed: 1, cancelled: 0 }, 1440, { group: 0, tier: 0, birthday: 360 }], "1–5 ต.ค.");
  const c = await report(o, "2026-10-01", "2026-10-01");
  ck.eq([c.status, c.json.counts], [200, { confirmed: 0, completed: 0, cancelled: 0 }], "1 ต.ค. (ไม่ดึง B13 ข้ามวัน)");
});
T("R10", "ตั้งเวลาถึงนัด B01 (12 ต.ค. 14:00) → กดเสร็จ → ยอด ต.ค. = Σ ยอดตารางคิวของนัดใช้บริการแล้ว", "[D:CR-05] ① [E sql:q_money] B01 total 1000", async (ck) => {
  await reset("2026-10-12T14:00:00+07:00");
  const o = await login("OWNER");
  const q = await o.get("/api/admin/bookings?date=2026-10-12");
  const b01 = (q.json.bookings ?? []).find((b) => b.code === "B01");
  ck.ok(b01, "เจอ B01 ในคิว 12 ต.ค.");
  if (!b01) return;
  const done = await o.post(`/api/admin/bookings/${b01.id}/complete`, {});
  ck.eq(done.status, 200, "กดเสร็จ B01");
  const r = await report(o, "2026-10-01", "2026-10-31");
  ck.eq(r.json.counts, { confirmed: 5, completed: 2, cancelled: 0 }, "counts");
  ck.eq([r.json.revenue, r.json.pendingValue], [1440 + 1000, 11130 - 1000], "revenue / pending");
  // ตรวจไขว้กับตารางคิวหลังร้าน (API เดิม) ทุกวันในช่วง
  let sum = 0;
  let pts = 0;
  for (let d = "2026-10-01"; d <= "2026-10-31"; d = addDays(d, 1)) {
    const day = await o.get(`/api/admin/bookings?date=${d}`);
    for (const b of day.json.bookings ?? []) if (b.status === "completed") {
      sum += Math.round(b.total * 100);
      pts += b.pointsEarned;
    }
  }
  ck.eq(r.json.revenue, sum / 100, "revenue = Σ ตารางคิว");
  ck.eq(r.json.pointsEarned, pts, "pointsEarned = Σ ตารางคิว");
});
T("R11", "ข้อความ REPORT_RANGE 3 ภาษา", "[D:CR-05] ② 422 · CLAUDE.md ข้อ 8", async (ck) => {
  for (const lang of ["th", "en", "zh"]) rangeErr(ck, await report(await login("OWNER", lang), "2026-10-31", "2026-10-01"), lang, `${lang} `);
});
T("R12", "แชท owner \"รายงานยอดขาย\" → ไม่เปิดเผยตัวเลขรายงาน", "CLAUDE.md ข้อ 8 · CR \"เห็นได้เฉพาะเจ้าของร้าน\"", async (ck) => {
  const o = await login("OWNER");
  const r = await o.post("/api/chat", { message: "รายงานยอดขายเดือนกันยายน", state: null, lang: "th" });
  ck.eq(r.status, 200, "status");
  const reply = String(r.json.reply ?? "");
  ck.ok(!/1,?900|11,?130|3,?340/.test(reply), `คำตอบไม่มีตัวเลขรายงาน (ได้ ${JSON.stringify(reply.slice(0, 80))})`);
});

// ── รัน ──
const only = process.argv.slice(2);
const run = only.length ? results.filter((t) => only.includes(t.id)) : results;
let pass = 0;
const failed = [];
const t0 = Date.now();
for (const t of run) {
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
console.log(`\nCR-05: ผ่าน ${pass}/${run.length}${failed.length ? ` · ล้ม ${failed.join(" ")}` : ""} · ${((Date.now() - t0) / 1000).toFixed(1)} วิ`);
process.exit(failed.length ? 1 : 0);
