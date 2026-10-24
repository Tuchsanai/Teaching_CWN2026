// CR-02 ส่วนลดกลุ่มขั้นบันได (มีผล "วันที่จอง" ตั้งแต่ 1 พ.ย. 2026 00:00 เวลาไทย)
//   ใช้ (PowerShell จากโฟลเดอร์บท): node tests/cr02.mjs          (ค่าเริ่ม BASE_URL=http://localhost:4000)
//   ต้องเปิด ALLOW_TEST_RESET=1 · reset เองทุกเคส (POST /api/test/reset {now}) · เลื่อนนาฬิกาด้วย POST /api/test/clock {now}
//   ค่าที่คาดหวังคิดมือใน docs/impact/CR-02.md §3 · ป้าย [D:CR-02] = CR + คำตอบร้าน · [E …] = ล็อกพฤติกรรมเดิม
//   Node >= 22 · ไม่มี dependency

const BASE = (process.env.BASE_URL || "http://localhost:4000").replace(/\/$/, "");
const USERS = {
  U06: ["vipa@sabai.test", "Vipa@2026"], // Platinum 10%
  U07: ["kan@sabai.test", "Kan@2026"], // Gold 5% (ยอดสะสม ฿10,000 พอดี)
  U08: ["liwei@sabai.test", "LiWei@2026"], // Silver 0%
  OWNER: ["owner@sabai.test", "Owner@2026"],
};

const BEFORE = "2026-10-31T23:59:00+07:00"; // 1 นาทีก่อนวันมีผล
const START = "2026-11-01T00:00:00+07:00"; // วันมีผลพอดี
const NOV1 = "2026-11-01T10:00:00+07:00";
const DEFAULT_NOW = "2026-10-10T10:00:00+07:00"; // วันที่ล็อกของชุดทดสอบเดิม
const APPT = "2026-11-05";

class Client {
  constructor() {
    this.cookie = "";
  }
  async req(method, path, body) {
    const headers = { "Content-Type": "application/json", "Accept-Language": "th" };
    if (this.cookie) headers.Cookie = this.cookie;
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
async function reset(now) {
  const r = await new Client().post("/api/test/reset", { now });
  if (r.status !== 200) throw new Error(`reset ${now}: ${r.status} ${JSON.stringify(r.json)}`);
}
async function setClock(now) {
  const r = await new Client().post("/api/test/clock", { now });
  if (r.status !== 200) throw new Error(`clock ${now}: ${r.status} ${JSON.stringify(r.json)}`);
}

const grp = (people, extra = {}) => ({ type: "group", serviceCode: "S01", people, date: APPT, time: "14:00", ...extra });

const results = [];
async function T(id, name, src, fn) {
  const fails = [];
  const eq = (actual, expected, label) => {
    if (JSON.stringify(actual) !== JSON.stringify(expected)) fails.push(`${label}: ได้ ${JSON.stringify(actual)} ควรเป็น ${JSON.stringify(expected)}`);
  };
  try {
    await fn(eq);
  } catch (e) {
    fails.push(`exception: ${e.message}`);
  }
  results.push({ id, name, src, ok: fails.length === 0, fails });
  console.log(`${fails.length ? "FAIL" : "PASS"} ${id} ${name} ${src}${fails.length ? "\n     - " + fails.join("\n     - ") : ""}`);
}

/** ราคาจากใบสรุป → ตรวจยอด/ชนิด/% */
async function quote(eq, client, body, want) {
  const r = await client.post("/api/price", body);
  eq(r.status, 200, "status");
  eq(r.json.total, want.total, "total");
  if (want.kind) eq(r.json.discountKind, want.kind, "discountKind");
  if (want.pct !== undefined) eq(r.json.discountPct, want.pct, "discountPct");
  return r;
}

/** ใบสรุป → จองจริงด้วย quotedTotal เดียวกัน (ยอดที่เก็บ = ยอดที่เห็น) */
async function quoteAndBook(eq, client, body, want) {
  const q = await quote(eq, client, body, want);
  const b = await client.post("/api/bookings", { ...body, quotedTotal: q.json.total });
  eq(b.status, 201, "booking status");
  eq(b.json.total, want.total, "booking total");
  return b;
}

// ── อัตราใหม่ (จอง 1 พ.ย. 10:00 · Silver) ────────────────────────────────
await T("C1", "กลุ่ม 2 คน → 422 GROUP_TOO_SMALL", "[D:CR-02] กฎอื่นเหมือนเดิม + ⚠️A1", async (eq) => {
  await reset(NOV1);
  const r = await (await login("U08")).post("/api/price", grp(2));
  eq(r.status, 422, "status");
  eq(r.json.error, "GROUP_TOO_SMALL", "error");
});
await T("C2", "กลุ่ม 3 คน ฿3,000 − 5% = ฿2,850 (จองจริง)", "[D:CR-02] ③#1", async (eq) => {
  await reset(NOV1);
  await quoteAndBook(eq, await login("U08"), grp(3), { total: 2850, kind: "group", pct: 5 });
});
await T("C3", "กลุ่ม 4 คน ฿4,000 − 10% = ฿3,600", "[D:CR-02] 10% เท่าเดิม", async (eq) => {
  await reset(NOV1);
  await quoteAndBook(eq, await login("U08"), grp(4), { total: 3600, kind: "group", pct: 10 });
});
await T("C4", "กลุ่ม 5 คน ฿5,000 − 15% = ฿4,250 (จองจริง)", "[D:CR-02] ③#2", async (eq) => {
  await reset(NOV1);
  await quoteAndBook(eq, await login("U08"), grp(5), { total: 4250, kind: "group", pct: 15 });
});
await T("C5", "กลุ่ม 6 คน ฿6,000 − 15% = ฿5,100 (จองจริง)", "[D:CR-02] 5–6 คน 15%", async (eq) => {
  await reset(NOV1);
  await quoteAndBook(eq, await login("U08"), grp(6), { total: 5100, kind: "group", pct: 15 });
});
await T("C6", "กลุ่ม 7 คน → 422 GROUP_CALL_SHOP", "[D:CR-02] 7+ โทรร้าน", async (eq) => {
  await reset(NOV1);
  const r = await (await login("U08")).post("/api/price", grp(7));
  eq(r.status, 422, "status");
  eq(r.json.error, "GROUP_CALL_SHOP", "error");
});

// ── ขอบวันมีผล ─────────────────────────────────────────────────────────────
await T("C7", "จอง 31 ต.ค. 23:59 กลุ่ม 3 → ฿3,000 ไม่มีส่วนลด", "[D:CR-02] ③#3", async (eq) => {
  await reset(BEFORE);
  await quoteAndBook(eq, await login("U08"), grp(3), { total: 3000, kind: "none", pct: 0 });
});
await T("C7b", "จอง 31 ต.ค. 23:59 กลุ่ม 5 → ฿4,500 (10% เดิม)", "[D:CR-02] ก่อนหน้านั้นราคาเดิม", async (eq) => {
  await reset(BEFORE);
  await quote(eq, await login("U08"), grp(5), { total: 4500, kind: "group", pct: 10 });
});
await T("C8", "จอง 1 พ.ย. 00:00 กลุ่ม 3 → ฿2,850", "[D:CR-02] เริ่ม 00:00 เวลาไทย", async (eq) => {
  await reset(START);
  await quote(eq, await login("U08"), grp(3), { total: 2850, kind: "group", pct: 5 });
});

// ── เลือกส่วนลดที่มากที่สุด ───────────────────────────────────────────────
await T("C9", "Gold 5% กลุ่ม 3 (5%) เท่ากัน → ขึ้นเป็นส่วนลดกลุ่ม ฿2,850", "[D:CR-02] คำตอบ ① ลำดับเดิม", async (eq) => {
  await reset(NOV1);
  await quote(eq, await login("U07"), grp(3), { total: 2850, kind: "group", pct: 5 });
});
await T("C10", "Platinum 10% กลุ่ม 3 (5%) → ระดับชนะ ฿2,700", "[D:CR-02] เลือกอันที่มากที่สุด", async (eq) => {
  await reset(NOV1);
  await quote(eq, await login("U06"), grp(3), { total: 2700, kind: "tier", pct: 10 });
});
await T("C11", "Platinum 10% กลุ่ม 5 (15%) → กลุ่มชนะ ฿4,250", "[D:CR-02] เลือกอันที่มากที่สุด", async (eq) => {
  await reset(NOV1);
  await quote(eq, await login("U06"), grp(5), { total: 4250, kind: "group", pct: 15 });
});

// ── แพ็กเกจ · รถ · บริการอื่น ──────────────────────────────────────────────
await T("C12", "แพ็กเกจ P01 4 คน ฿2,900 × 4 = ฿11,600 ไม่มีส่วนลด", "[D:CR-02] Bangkok Relax ไม่มีส่วนลดกลุ่ม", async (eq) => {
  await reset(NOV1);
  await quote(eq, await login("U08"), { type: "package", serviceCode: "P01", people: 4, date: APPT, time: "13:00" }, { total: 11600, kind: "none", pct: 0 });
});
await T("C13", "กลุ่ม 6 + H04 12 กม. ฿6,000 − 15% + รถ 2×฿300 = ฿5,700", "[D:CR-02] + ลำดับราคาเดิม", async (eq) => {
  await reset(NOV1);
  await quote(eq, await login("U08"), grp(6, { hotelCode: "H04" }), { total: 5700, kind: "group", pct: 15 });
});
await T("C14", "กลุ่ม 3 S03 ฿3,600 − 5% (฿180) = ฿3,420", "[D:CR-02]", async (eq) => {
  await reset(NOV1);
  await quote(eq, await login("U08"), grp(3, { serviceCode: "S03" }), { total: 3420, kind: "group", pct: 5 });
});

// ── นัดที่บันทึกแล้วไม่เปลี่ยนยอด ──────────────────────────────────────────
await T("C15", "จอง 31 ต.ค. 23:59 กลุ่ม 5 นัด 5 พ.ย. → นาฬิกา 1 พ.ย. ยอดในคิวยัง ฿4,500", "[D:CR-02] ห้ามเปลี่ยนยอด", async (eq) => {
  await reset(BEFORE);
  const b = await quoteAndBook(eq, await login("U08"), grp(5), { total: 4500, kind: "group", pct: 10 });
  await setClock(NOV1);
  const q = await (await login("OWNER")).get(`/api/admin/bookings?date=${APPT}`);
  const row = (q.json.bookings || []).find((x) => x.code === b.json.code);
  eq(q.json.today, "2026-11-01", "today หลังเลื่อนนาฬิกา");
  eq(row?.total, 4500, `ยอด ${b.json.code}`);
});
await T("C16", "B04 (seed จอง 8 ต.ค.) → นาฬิกา 1 พ.ย. ยัง ฿4,500", "[D:CR-02] ไม่ย้อนแก้นัดเก่า", async (eq) => {
  await reset(DEFAULT_NOW);
  await setClock(NOV1);
  const q = await (await login("OWNER")).get("/api/admin/bookings?date=2026-10-14");
  eq(q.json.bookings?.find((x) => x.code === "B04")?.total, 4500, "B04 total");
});
await T("C17", "ใบสรุป 31 ต.ค. 23:59 (฿3,000) ยืนยัน 1 พ.ย. 00:00 → 409 PRICE_CHANGED ฿2,850", "[D:CR-02] คำตอบ ①", async (eq) => {
  await reset(BEFORE);
  const c = await login("U08");
  const q = await c.post("/api/price", grp(3));
  eq(q.json.total, 3000, "ใบสรุปก่อนเที่ยงคืน");
  await setClock(START);
  const b = await c.post("/api/bookings", { ...grp(3), quotedTotal: q.json.total });
  eq(b.status, 409, "status");
  eq(b.json.error, "PRICE_CHANGED", "error");
  eq(b.json.total, 2850, "ยอดใหม่ที่แจ้ง");
});

// ── ล็อกของเดิม (จอง 10 ต.ค. = ก่อนวันมีผล) ──────────────────────────────
await T("C18", "จอง 10 ต.ค. กลุ่ม 3/4/5 = ฿3,000/฿3,600/฿4,500 · กลุ่ม 6 + H04 = ฿6,000", "[E golden/price.json:a485c485] [E check-rules E26 E27 E28 E79]", async (eq) => {
  await reset(DEFAULT_NOW);
  const c = await login("U08");
  const d = { date: "2026-10-22" };
  await quote(eq, c, grp(3, d), { total: 3000, kind: "none" });
  await quote(eq, c, grp(4, d), { total: 3600, kind: "group", pct: 10 });
  await quote(eq, c, grp(5, d), { total: 4500, kind: "group", pct: 10 });
  await quote(eq, c, grp(6, { ...d, hotelCode: "H04" }), { total: 6000, kind: "group", pct: 10 });
});

await reset(DEFAULT_NOW); // คืนข้อมูลทดสอบเป็นค่าเริ่ม
const pass = results.filter((r) => r.ok).length;
console.log(`\nCR-02: ${pass}/${results.length} ผ่าน · ล้ม: ${results.filter((r) => !r.ok).map((r) => r.id).join(" ") || "-"}`);
process.exit(pass === results.length ? 0 : 1);
