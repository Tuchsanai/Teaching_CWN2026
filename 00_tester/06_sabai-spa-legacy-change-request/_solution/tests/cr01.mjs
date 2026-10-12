// CR-01 ลูกค้าเลื่อนนัดเอง · ขั้น A POST /api/bookings/:id/reschedule · ขั้น B GET /api/bookings/:id/reschedule-slots?date=
//   ใช้ (PowerShell จากโฟลเดอร์บท): node tests/cr01.mjs          (ค่าเริ่ม BASE_URL=http://localhost:4000)
//   ต้องเปิด ALLOW_TEST_RESET=1 · reset ก่อนทุกเคส (วันนี้ = 10 ต.ค. 2026 10:00 เว้นแต่เคสระบุ)
//   ค่าที่คาดหวังจาก docs/impact/CR-01.md §5 · ป้าย [D:CR-01] = CR + คำตอบร้าน · [D:CR-03]/[D:CR-04] = กฎ CR ก่อนหน้า · [E] = ค่าเดิมก่อนแก้
//   Node >= 22 · ไม่มี dependency

const BASE = (process.env.BASE_URL || "http://localhost:4000").replace(/\/$/, "");
const TODAY = "2026-10-10T10:00:00+07:00";
const USERS = {
  NIDA: ["nida@sabai.test", "Nida@2026"],
  TON: ["ton@sabai.test", "Ton@2026"],
  FON: ["fon@sabai.test", "Fon@2026"],
  PRAE: ["prae@sabai.test", "Prae@2026"],
  KAN: ["kan@sabai.test", "Kan@2026"],
  LIWEI: ["liwei@sabai.test", "LiWei@2026"],
  OWNER: ["owner@sabai.test", "Owner@2026"],
};
const PHONE = "02-123-4567";
const MSG_TOO_LATE = {
  th: `เลื่อนนัดเองได้เมื่อเหลือเวลาก่อนนัดอย่างน้อย 24 ชั่วโมง กรุณาโทร ${PHONE}`,
  en: `You can reschedule up to 24 hours before your appointment. Please call ${PHONE}`,
  zh: `距预约不足24小时，无法自行改期，请致电 ${PHONE}`,
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
const ID = { B01: 1, B02: 2, B04: 4, B05: 5, B06: 6, B07: 7, B11: 11 };
const rs = (c, code, date, time) => c.post(`/api/bookings/${ID[code] ?? code}/reschedule`, { date, time });
const rsSlots = (c, code, date) => c.get(`/api/bookings/${ID[code] ?? code}/reschedule-slots?date=${date}`);
const slots = (c, date, service = "S01", type = "single", people = 1) =>
  c.get(`/api/slots?${new URLSearchParams({ service, date, type, people: String(people) })}`);
async function mine(c, code) {
  const r = await c.get("/api/me/bookings");
  return (r.json.bookings ?? []).find((b) => b.code === code);
}
async function ownerQueue(date) {
  const o = await login("OWNER");
  const r = await o.get(`/api/admin/bookings?date=${date}`);
  return (r.json.bookings ?? []).filter((b) => b.status !== "cancelled");
}
/** ใบเสนอราคา → จองด้วย quotedTotal (สมาชิกหรือแขก) */
async function book(c, body) {
  const q = await c.post("/api/price", body);
  if (q.status !== 200) throw new Error(`price ${q.status} ${JSON.stringify(q.json)}`);
  const r = await c.post("/api/bookings", { ...body, quotedTotal: q.json.total });
  if (r.status !== 201) throw new Error(`book ${r.status} ${JSON.stringify(r.json)}`);
  return r.json;
}

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
const err = (ck, r, status, code, what = "") => {
  ck.eq(r.status, status, `${what}status`);
  ck.eq(r.json.error, code, `${what}error`);
};

T("R1", "นิดา B05 → 12 ต.ค. 10:00 (เหลือ 24 ชม. พอดี) → 200 ฿760 เดิม · รหัส/แถวเดิม", "[D:CR-01] ③1 ① · ฿760 [E]", async (ck) => {
  const c = await login("NIDA");
  const r = await rs(c, "B05", "2026-10-12", "10:00");
  ck.eq(r.status, 200, "status");
  ck.eq(
    [r.json.ok, r.json.code, r.json.date, r.json.time, r.json.endTime, r.json.therapists, r.json.total],
    [true, "B05", "2026-10-12", "10:00", "11:00", ["T04"], 760],
    "body",
  );
  const b = await mine(c, "B05");
  ck.eq([b?.date, b?.time, b?.endTime, b?.total, b?.status], ["2026-10-12", "10:00", "11:00", 760, "confirmed"], "นัดของฉัน B05");
  const all = (await c.get("/api/me/bookings")).json.bookings ?? [];
  ck.eq(all.length, 8, "จำนวนนัดของนิดา (ไม่มีนัดใหม่/ไม่มี cancelled เพิ่ม)");
});
T("R2", "เหมือน R1 แต่ตอน 10 ต.ค. 10:01 → 422 RESCHEDULE_TOO_LATE + phone · B05 ยัง 11 ต.ค.", "[D:CR-01] ③2 ②", async (ck) => {
  await reset("2026-10-10T10:01:00+07:00");
  const c = await login("NIDA");
  const r = await rs(c, "B05", "2026-10-12", "10:00");
  err(ck, r, 422, "RESCHEDULE_TOO_LATE");
  ck.eq(r.json.phone, PHONE, "phone");
  ck.eq(r.json.message, MSG_TOO_LATE.th, "message th");
  const b = await mine(c, "B05");
  ck.eq([b?.date, b?.time], ["2026-10-11", "10:00"], "B05 ไม่เปลี่ยน");
});
T("R3", "นิดา B06 (วันนี้ 15:00) → 422 RESCHEDULE_TOO_LATE", "[D:CR-01] CR ข้อ 1", async (ck) => {
  err(ck, await rs(await login("NIDA"), "B06", "2026-10-12", "15:00"), 422, "RESCHEDULE_TOO_LATE");
});
T("R4", "นิดา B05 → 11 ต.ค. 10:00 (เวลาเดิม) → 422 RESCHEDULE_SAME", "[D:CR-01] ① ②", async (ck) => {
  err(ck, await rs(await login("NIDA"), "B05", "2026-10-11", "10:00"), 422, "RESCHEDULE_SAME");
});
T("R5", "นิดา B05 → 11 ต.ค. 14:00 (วันเดิมคนละเวลา) → 200", "[D:CR-01] ①", async (ck) => {
  const r = await rs(await login("NIDA"), "B05", "2026-10-11", "14:00");
  ck.eq([r.status, r.json.date, r.json.time], [200, "2026-10-11", "14:00"], "status/date/time");
});
T("R6", "นิดา B05 → 9 พ.ย. 200 · 10 พ.ย. 422 DATE_OUT_OF_RANGE", "[D:CR-01] CR ข้อ 3 ②", async (ck) => {
  const c = await login("NIDA");
  const out = await rs(c, "B05", "2026-11-10", "10:00");
  err(ck, out, 422, "DATE_OUT_OF_RANGE", "10 พ.ย. ");
  ck.eq([out.json.min, out.json.max], ["2026-10-11", "2026-11-09"], "ช่วงวัน");
  const r = await rs(c, "B05", "2026-11-09", "10:00");
  ck.eq(r.status, 200, "9 พ.ย. status");
});
T("R7", "นิดา B05 (60 นาที) → 12 ต.ค. 21:00 200 · 21:30 422 SLOT_INVALID", "[D:CR-01] CR ข้อ 3", async (ck) => {
  const c = await login("NIDA");
  err(ck, await rs(c, "B05", "2026-10-12", "21:30"), 422, "SLOT_INVALID", "21:30 ");
  const r = await rs(c, "B05", "2026-10-12", "21:00");
  ck.eq([r.status, r.json.endTime], [200, "22:00"], "21:00");
});
T("R8", "ฝน B01 (T03) → 14 ต.ค. 16:00 → 409 SLOT_TAKEN (T03 ติด B04) · B01 ไม่เปลี่ยน", "[D:CR-01] CR ข้อ 4", async (ck) => {
  const c = await login("FON");
  err(ck, await rs(c, "B01", "2026-10-14", "16:00"), 409, "SLOT_TAKEN");
  const b = await mine(c, "B01");
  ck.eq([b?.date, b?.time], ["2026-10-12", "14:00"], "B01 ไม่เปลี่ยน");
});
T("R9", "reschedule-slots B01 14 ต.ค. ไม่มี 16:00 · /api/slots S01 14 ต.ค. 16:00 ยังว่าง", "[D:CR-01] ② · [E]", async (ck) => {
  const c = await login("FON");
  const r = await rsSlots(c, "B01", "2026-10-14");
  ck.eq(r.status, 200, "status");
  const s = r.json.slots ?? [];
  ck.eq(s.length, 23, "จำนวนรอบ 60 นาที");
  ck.eq(s.find((x) => x.time === "16:00")?.available, false, "16:00 เลื่อนได้?");
  ck.eq(s.find((x) => x.time === "15:00")?.available, true, "15:00 เลื่อนได้?");
  const g = await slots(c, "2026-10-14");
  ck.eq(g.json.slots?.find((x) => x.time === "16:00")?.available, true, "/api/slots 16:00 [E]");
});
T("R10", "ต้น B02 คู่ 19:00 → 19:30 วันเดียวกัน (ทับเวลาตัวเอง) → 200 คนเดิม 2 คน", "[D:CR-01] ①", async (ck) => {
  const c = await login("TON");
  const r = await rs(c, "B02", "2026-10-17", "19:30");
  ck.eq([r.status, r.json.time, r.json.endTime, r.json.therapists], [200, "19:30", "21:00", ["T01", "T02"]], "body");
  const q = (await ownerQueue("2026-10-17")).find((b) => b.code === "B02");
  ck.eq(q?.time, "19:30–21:00", "คิวร้าน B02");
});
T("R11", "reschedule-slots B02 17 ต.ค.: 19:30 ว่าง (ไม่นับตัวเอง) · 19:00 = current", "[D:CR-01] ② ①", async (ck) => {
  const r = await rsSlots(await login("TON"), "B02", "2026-10-17");
  ck.eq(r.status, 200, "status");
  const s = r.json.slots ?? [];
  ck.eq(s.find((x) => x.time === "19:30")?.available, true, "19:30");
  const cur = s.find((x) => x.time === "19:00");
  ck.eq([cur?.available, cur?.current], [false, true], "19:00 current");
  ck.eq(s.some((x) => x.time === "21:00"), false, "90 นาทีไม่มีรอบ 21:00");
});
T("R12", "B05 โดย ต้น 403 · ไม่ล็อกอิน 401 · owner 403 · B05 ไม่เปลี่ยน", "[D:CR-01] CR ข้อ 7 ① ②", async (ck) => {
  err(ck, await rs(await login("TON"), "B05", "2026-10-12", "10:00"), 403, "FORBIDDEN", "ต้น ");
  err(ck, await rs(new Client(), "B05", "2026-10-12", "10:00"), 401, "LOGIN_REQUIRED", "ไม่ล็อกอิน ");
  err(ck, await rs(await login("OWNER"), "B05", "2026-10-12", "10:00"), 403, "FORBIDDEN", "owner ");
  err(ck, await rsSlots(await login("TON"), "B05", "2026-10-12"), 403, "FORBIDDEN", "slots ต้น ");
  const b = await mine(await login("NIDA"), "B05");
  ck.eq([b?.date, b?.time], ["2026-10-11", "10:00"], "B05 ไม่เปลี่ยน");
});
T("R13", "แพร B07 (completed) · นิดา B11 (cancelled) → 422 RESCHEDULE_NOT_ALLOWED", "[D:CR-01] CR ข้อ 1 ②", async (ck) => {
  err(ck, await rs(await login("PRAE"), "B07", "2026-10-12", "10:00"), 422, "RESCHEDULE_NOT_ALLOWED", "B07 ");
  err(ck, await rs(await login("NIDA"), "B11", "2026-10-12", "10:00"), 422, "RESCHEDULE_NOT_ALLOWED", "B11 ");
});
T("R14", "ต้น จองเดือนเกิด 31 ต.ค. → 1 พ.ย. 422 RESCHEDULE_BIRTHDAY · → 30 ต.ค. 200 ส่วนลดเดิม", "[D:CR-01] CR ข้อ 5 ②", async (ck) => {
  const c = await login("TON");
  const nb = await book(c, { type: "single", serviceCode: "S01", people: 1, date: "2026-10-31", time: "10:00", useBirthday: true });
  ck.eq(nb.quote?.discountKind, "birthday", "จองด้วยเดือนเกิด");
  err(ck, await rs(c, nb.bookingId, "2026-11-01", "10:00"), 422, "RESCHEDULE_BIRTHDAY", "1 พ.ย. ");
  err(ck, await rsSlots(c, nb.bookingId, "2026-11-01"), 422, "RESCHEDULE_BIRTHDAY", "slots 1 พ.ย. ");
  const r = await rs(c, nb.bookingId, "2026-10-30", "10:00");
  ck.eq([r.status, r.json.total], [200, nb.total], "30 ต.ค. ยอดเดิม");
  const b = await mine(c, nb.code);
  ck.eq([b?.date, b?.total], ["2026-10-30", nb.total], "นัดของฉัน");
});
T("R15", "กัน คอร์ส C02 19 ต.ค. → 21 ต.ค. 422 COURSE_UNAVAILABLE reserved 1 · → 20 ต.ค. 200 reserved 1", "[D:CR-01] ③3 · BR-14 [E]", async (ck) => {
  const c = await login("KAN");
  const nb = await book(c, { type: "course", serviceCode: "K01", people: 1, date: "2026-10-19", time: "10:00" });
  const reserved = async () => (await c.get("/api/wallet")).json.courses?.find((x) => x.code === "C02")?.reserved;
  ck.eq(await reserved(), 1, "reserved หลังจอง");
  err(ck, await rs(c, nb.bookingId, "2026-10-21", "10:00"), 422, "COURSE_UNAVAILABLE", "21 ต.ค. ");
  ck.eq(await reserved(), 1, "reserved หลังเลื่อนไม่ได้");
  ck.eq((await mine(c, nb.code))?.date, "2026-10-19", "นัดยัง 19 ต.ค.");
  const r = await rs(c, nb.bookingId, "2026-10-20", "10:00");
  ck.eq(r.status, 200, "20 ต.ค. (วันหมดอายุ)");
  ck.eq(await reserved(), 1, "reserved หลังเลื่อนสำเร็จ");
});
T("R16", "ฝน จองใช้แต้ม 2 ก้อน 13 ต.ค. → เลื่อน 15 ต.ค. · ยอด/แต้มคงเหลือไม่เปลี่ยน", "[D:CR-01] CR ข้อ 2 · [E]", async (ck) => {
  const c = await login("FON");
  const nb = await book(c, { type: "single", serviceCode: "S01", people: 1, date: "2026-10-13", time: "11:00", redeemBlocks: 2 });
  const pts = async () => (await c.get("/api/me")).json.points;
  const before = await pts();
  ck.eq(before, 50, "แต้มหลังจอง (250 − 200)");
  const r = await rs(c, nb.bookingId, "2026-10-15", "11:00");
  ck.eq([r.status, r.json.total], [200, nb.total], "ยอดเดิม");
  ck.eq(await pts(), before, "แต้มคงเหลือ");
  const b = await mine(c, nb.code);
  ck.eq([b?.date, b?.total], ["2026-10-15", nb.total], "นัดของฉัน");
});
T("R17", "หลังเลื่อน B05: รอบ 11 ต.ค. 10:00 ของ T04 ว่าง · แขกจอง T04 ได้ 201", "[D:CR-01] ③1 CR ข้อ 6 · [E]", async (ck) => {
  const g = new Client();
  const before = (await slots(g, "2026-10-11", "S05")).json.slots?.find((x) => x.time === "10:00");
  ck.eq(before?.therapists?.some((t) => t.code === "T04"), false, "ก่อนเลื่อน T04 ไม่ว่าง [E]");
  ck.eq((await rs(await login("NIDA"), "B05", "2026-10-12", "10:00")).status, 200, "เลื่อน");
  const after = (await slots(g, "2026-10-11", "S05")).json.slots?.find((x) => x.time === "10:00");
  ck.eq(after?.therapists?.some((t) => t.code === "T04"), true, "หลังเลื่อน T04 ว่าง");
  const body = { type: "single", serviceCode: "S05", people: 1, date: "2026-10-11", time: "10:00", therapists: ["T04"], contactName: "แขกทดสอบ", contactPhone: "0899990101" };
  const q = await g.post("/api/price", body);
  const r = await g.post("/api/bookings", { ...body, quotedTotal: q.json.total });
  ck.eq(r.status, 201, "แขกจอง T04 11 ต.ค. 10:00");
});
T("R18", "นิดามีนัด 12 ต.ค. 10:00 อยู่แล้ว → เลื่อน B05 ไปทับ → 409 DUPLICATE_BOOKING", "[D:CR-03] BR-21", async (ck) => {
  const c = await login("NIDA");
  const nb = await book(c, { type: "single", serviceCode: "S01", people: 1, date: "2026-10-12", time: "10:00" });
  const r = await rs(c, "B05", "2026-10-12", "10:00");
  err(ck, r, 409, "DUPLICATE_BOOKING");
  ck.eq(r.json.existing, nb.code, "existing");
});
T("R19", "นิดา B05 → 23 ต.ค. (วันปิยมหาราช) → 422 SHOP_CLOSED", "[D:CR-04]", async (ck) => {
  err(ck, await rs(await login("NIDA"), "B05", "2026-10-23", "10:00"), 422, "SHOP_CLOSED");
});
T("R20", "RESCHEDULE_TOO_LATE ข้อความ en / zh", "[D:CR-01] ②", async (ck) => {
  for (const lang of ["en", "zh"]) {
    const r = await rs(await login("NIDA", lang), "B06", "2026-10-12", "15:00");
    err(ck, r, 422, "RESCHEDULE_TOO_LATE", `${lang} `);
    ck.eq(r.json.message, MSG_TOO_LATE[lang], `${lang} message`);
  }
});
T("R21", "นิดา B05 เลื่อน 2 ครั้ง 12 ต.ค. → 13 ต.ค. → 200 ทั้งคู่", "[D:CR-01] ①", async (ck) => {
  const c = await login("NIDA");
  ck.eq((await rs(c, "B05", "2026-10-12", "10:00")).status, 200, "ครั้งที่ 1");
  ck.eq((await rs(c, "B05", "2026-10-13", "10:00")).status, 200, "ครั้งที่ 2");
  ck.eq((await mine(c, "B05"))?.date, "2026-10-13", "วันใหม่");
});
T("R22", "หลี่เว่ย B04 กลุ่ม 5 คน → 15 ต.ค. 16:00 → 200 นักบำบัด T01–T05 เดิม", "[D:CR-01] ①", async (ck) => {
  const r = await rs(await login("LIWEI"), "B04", "2026-10-15", "16:00");
  ck.eq([r.status, r.json.therapists], [200, ["T01", "T02", "T03", "T04", "T05"]], "body");
});

// ── รัน ──
const only = process.argv.slice(2);
let pass = 0;
const failed = [];
const t0 = Date.now();
for (const t of results.filter((x) => !only.length || only.includes(x.id))) {
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
const n = results.filter((x) => !only.length || only.includes(x.id)).length;
console.log(`\nCR-01: ผ่าน ${pass}/${n}${failed.length ? ` · ล้ม ${failed.join(" ")}` : ""} · ${((Date.now() - t0) / 1000).toFixed(1)} วิ`);
process.exit(failed.length ? 1 : 0);
