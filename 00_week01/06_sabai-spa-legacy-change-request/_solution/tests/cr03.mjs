// CR-03 กันจองซ้ำของคนเดียวกัน (เรื่องร้องเรียน · BR-21)
//   ใช้ (PowerShell จากโฟลเดอร์บท): node tests/cr03.mjs          (ค่าเริ่ม BASE_URL=http://localhost:4000)
//   ต้องเปิด ALLOW_TEST_RESET=1 · reset ก่อนทุกเคส (วันนี้ = 10 ต.ค. 2026 10:00)
//   ค่าที่คาดหวังจาก docs/impact/CR-03.md §3 · ป้าย [D:CR-03] = CR + คำตอบร้าน · [E …] = ล็อกพฤติกรรมเดิม
//   ข้อความไทย/จีนส่งผ่าน node (ไม่ผ่าน PowerShell) · Node >= 22 · ไม่มี dependency

const BASE = (process.env.BASE_URL || "http://localhost:4000").replace(/\/$/, "");
const TODAY = "2026-10-10T10:00:00+07:00";
const USERS = {
  U01: ["nida@sabai.test", "Nida@2026"],
  U02: ["ton@sabai.test", "Ton@2026"],
  U03: ["may@sabai.test", "May@2026"],
  U04: ["fon@sabai.test", "Fon@2026"],
  OWNER: ["owner@sabai.test", "Owner@2026"],
};
const MSG = {
  th: (c) => `คุณมีนัดในช่วงเวลานี้อยู่แล้ว (รหัส ${c})`,
  en: (c) => `You already have a booking at this time (code ${c})`,
  zh: (c) => `您在该时段已有预约（预约号 ${c}）`,
};
const SLOT_TAKEN_TH = "เวลานี้ถูกจองแล้ว";

class Client {
  constructor(lang) {
    this.cookie = "";
    this.lang = lang; // ภาษาของ error มาจาก cookie lang (http.ts handle() → getLang())
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
      json = { raw: text };
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
async function reset() {
  const r = await new Client().post("/api/test/reset", { now: TODAY });
  if (r.status !== 200) throw new Error(`reset: ${r.status} ${JSON.stringify(r.json)}`);
}
/** ยอดจาก /api/price (ราคาเดิม ไม่ใช่สิ่งที่ CR-03 ตรวจ) แล้วจองด้วย quotedTotal นั้น */
async function book(c, body) {
  const q = await c.post("/api/price", body);
  if (q.status !== 200) return q;
  return c.post("/api/bookings", { ...body, quotedTotal: q.json.total });
}
async function queue(date) {
  const o = await login("OWNER");
  const r = await o.get(`/api/admin/bookings?date=${date}`);
  return r.json.bookings.filter((b) => b.status !== "cancelled");
}
const code = (r) => r.json?.code ?? r.json?.booking?.code;
const guest = (o) => ({ type: "single", serviceCode: "S02", people: 1, date: "2026-10-13", time: "10:00", contactName: "คุณสมชาย", contactPhone: "081-000-0003", ...o });

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
const dup = (ck, r, existing, lang = "th") => {
  ck.eq(r.status, 409, "status");
  ck.eq(r.json.error, "DUPLICATE_BOOKING", "error");
  ck.eq(r.json.existing, existing, "existing");
  ck.eq(r.json.message, MSG[lang](existing), "message");
};

T("C1", "ไม่ล็อกอิน ซ้ำนัดคุณสมชาย 081-000-0003 13 ต.ค. 10:00 → DUPLICATE_BOOKING B03 · คิวยังมี 1 นัด", "[D:CR-03] ③1", async (ck) => {
  const before = (await queue("2026-10-13")).length;
  const r = await book(new Client(), guest());
  dup(ck, r, "B03");
  const after = await queue("2026-10-13");
  ck.eq(after.length, before, "จำนวนนัด 13 ต.ค. ไม่เพิ่ม");
  ck.eq(after.filter((b) => b.time.startsWith("10:00") && b.customer.includes("081-000-0003")).length, 1, "นัดคุณสมชาย 10:00");
});
T("C2", "เบอร์ไม่มีขีด 0810000003 → DUPLICATE_BOOKING B03", "[D:CR-03] ③1", async (ck) => {
  dup(ck, await book(new Client(), guest({ contactPhone: "0810000003" })), "B03");
});
T("C3", "เบอร์ (081) 000 0003 · S01 11:00 ทับบางส่วน → DUPLICATE_BOOKING B03", "[D:CR-03] ①", async (ck) => {
  dup(ck, await book(new Client(), guest({ serviceCode: "S01", time: "11:00", contactPhone: "(081) 000 0003" })), "B03");
});
T("C4", "ต่อกันพอดี 11:30 → 201", "[D:CR-03] ③2", async (ck) => {
  const r = await book(new Client(), guest({ time: "11:30", contactPhone: "0810000003" }));
  ck.eq(r.status, 201, "status");
});
T("C5", "คนละเบอร์ 0899999999 10:00 → 201", "[D:CR-03] ③3", async (ck) => {
  const r = await book(new Client(), guest({ contactName: "คุณสมหญิง", contactPhone: "0899999999" }));
  ck.eq(r.status, 201, "status");
});
T("C6", "สมาชิก U01 S01 11 ต.ค. 10:30 ทับ B05 → DUPLICATE_BOOKING B05", "[D:CR-03] ①", async (ck) => {
  const u = await login("U01");
  dup(ck, await book(u, { type: "single", serviceCode: "S01", people: 1, date: "2026-10-11", time: "10:30" }), "B05");
});
T("C7", "ไม่ล็อกอิน เบอร์ตรงบัญชีนิดา 081-111-0001 11 ต.ค. 10:00 → 201 (ไม่เทียบข้ามสมาชิก/แขก)", "[D:CR-03] ①", async (ck) => {
  const r = await book(new Client(), guest({ serviceCode: "S01", date: "2026-10-11", contactName: "คุณนิดา", contactPhone: "081-111-0001" }));
  ck.eq(r.status, 201, "status");
});
T("C8", "สมาชิก U01 จอง 15 ต.ค. 10:00 → ยกเลิก → จองเวลาเดิม → 201", "[D:CR-03] ①", async (ck) => {
  const u = await login("U01");
  const body = { type: "single", serviceCode: "S01", people: 1, date: "2026-10-15", time: "10:00" };
  const a = await book(u, body);
  ck.eq(a.status, 201, "จองครั้งแรก");
  const c = await u.post(`/api/bookings/${code(a)}/cancel`, {});
  ck.eq(c.status, 200, "ยกเลิก");
  const b = await book(u, body);
  ck.eq(b.status, 201, "จองใหม่หลังยกเลิก");
});
T("C9", "คู่ (couple 2 คน) 13 ต.ค. 10:00 เบอร์คุณสมชาย → DUPLICATE_BOOKING B03", "[D:CR-03] ①", async (ck) => {
  dup(ck, await book(new Client(), guest({ type: "couple", people: 2 })), "B03");
});
T("C10", "ไม่ล็อกอิน กดพร้อมกัน 2 คำขอ 0855555555 14 ต.ค. 13:00 → [201, 409 DUPLICATE_BOOKING] · ฐานมี 1 นัด", "[D:CR-03] ②", async (ck) => {
  const body = guest({ serviceCode: "S01", date: "2026-10-14", time: "13:00", contactName: "คุณกดซ้ำ", contactPhone: "0855555555" });
  const q = await new Client().post("/api/price", body);
  const res = await Promise.all([1, 2].map(() => new Client().post("/api/bookings", { ...body, quotedTotal: q.json.total })));
  ck.eq(res.map((r) => r.status).sort(), [201, 409], "status ทั้งสองคำขอ");
  const win = res.find((r) => r.status === 201);
  const lost = res.find((r) => r.status === 409);
  if (win && lost) dup(ck, lost, code(win));
  const rows = (await queue("2026-10-14")).filter((b) => b.customer.includes("0855555555"));
  ck.eq(rows.length, 1, "นัดของเบอร์นี้ในฐาน");
});
T("C11", "สมาชิก U01 กดพร้อมกัน 2 คำขอ 16 ต.ค. 13:00 → [201, 409 DUPLICATE_BOOKING]", "[D:CR-03] ②", async (ck) => {
  const u = await login("U01");
  const body = { type: "single", serviceCode: "S01", people: 1, date: "2026-10-16", time: "13:00" };
  const q = await u.post("/api/price", body);
  const res = await Promise.all([1, 2].map(() => u.post("/api/bookings", { ...body, quotedTotal: q.json.total })));
  ck.eq(res.map((r) => r.status).sort(), [201, 409], "status ทั้งสองคำขอ");
  const win = res.find((r) => r.status === 201);
  const lost = res.find((r) => r.status === 409);
  if (win && lost) dup(ck, lost, code(win));
});
T("C12", "คนละคนพร้อมกัน U03+U04 T04 15 ต.ค. 11:00 → [201, 409 SLOT_TAKEN] (ของเดิม)", "[E check-rules E14] + [D:CR-03] ①", async (ck) => {
  const [a, b] = await Promise.all([login("U03"), login("U04")]);
  const body = { type: "single", serviceCode: "S01", date: "2026-10-15", time: "11:00", therapists: ["T04"], quotedTotal: 1000 };
  const res = await Promise.all([a.post("/api/bookings", body), b.post("/api/bookings", body)]);
  ck.eq(res.map((r) => r.status).sort(), [201, 409], "status ทั้งสองคำขอ");
  const lost = res.find((r) => r.status === 409);
  ck.eq(lost?.json.error, "SLOT_TAKEN", "error ตัวแพ้");
  ck.eq(lost?.json.message, SLOT_TAKEN_TH, "ข้อความตัวแพ้");
});
T("C13", "ข้อความอังกฤษ (cookie lang=en)", "[D:CR-03] ②", async (ck) => {
  dup(ck, await book(new Client("en"), guest({ lang: "en" })), "B03", "en");
});
T("C14", "ข้อความจีน (cookie lang=zh)", "[D:CR-03] ②", async (ck) => {
  dup(ck, await book(new Client("zh"), guest({ lang: "zh" })), "B03", "zh");
});

T("C17", "ลำดับ error: U02 (เจ้าของ B02 คู่ 17 ต.ค. 19:00–20:30) จองคู่ 19:30 → ห้องคู่เต็ม 409 SLOT_TAKEN แบบเดิม", "[E e2e-legacy TC-BOOK-07]", async (ck) => {
  const u = await login("U02");
  const r = await u.post("/api/bookings", { type: "couple", serviceCode: "S02", people: 2, date: "2026-10-17", time: "19:30", quotedTotal: 2520 });
  ck.eq(r.status, 409, "status");
  ck.eq(r.json.error, "SLOT_TAKEN", "error");
  ck.eq(r.json.message, SLOT_TAKEN_TH, "ข้อความ");
});
T("C18", "U02 จองเดี่ยว S01 17 ต.ค. 19:30 (นักบำบัดว่าง แต่ทับ B02 ของตัวเอง) → DUPLICATE_BOOKING B02", "[D:CR-03] ① ทุกแบบการจอง", async (ck) => {
  dup(ck, await book(await login("U02"), { type: "single", serviceCode: "S01", people: 1, date: "2026-10-17", time: "19:30" }), "B02");
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
T("C15", "แชทภาษาไทย จองซ้ำนัดคุณสมชาย → ข้อความไทย + B03 · ไม่มีนัดใหม่", "[D:CR-03] ① ②", async (ck) => {
  const before = (await queue("2026-10-13")).length;
  const r = await chatFlow("th", ["จองนวดไทย 90", "2026-10-13", "10:00", "สมชาย 081-000-0003", "ยืนยัน"]);
  ck.eq(r.status, 200, "status");
  ck.eq(r.json.reply, MSG.th("B03"), "คำตอบแชท");
  ck.eq(r.json.booking ?? null, null, "ไม่มี booking ในคำตอบ");
  ck.eq((await queue("2026-10-13")).length, before, "จำนวนนัด 13 ต.ค. ไม่เพิ่ม");
});
T("C16", "แชทภาษาจีน จองซ้ำด้วยเบอร์ไม่มีขีด → ข้อความจีน + B03", "[D:CR-03] ① ②", async (ck) => {
  const r = await chatFlow("zh", ["预约泰式按摩 90", "2026-10-13", "10:00", "李 0810000003", "确认"]);
  ck.eq(r.status, 200, "status");
  ck.eq(r.json.reply, MSG.zh("B03"), "คำตอบแชท");
  ck.eq(r.json.booking ?? null, null, "ไม่มี booking ในคำตอบ");
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
console.log(`\nCR-03: ผ่าน ${pass}/${results.length}${failed.length ? ` · ล้ม ${failed.join(" ")}` : ""} · ${((Date.now() - t0) / 1000).toFixed(1)} วิ`);
process.exit(failed.length ? 1 : 0);
