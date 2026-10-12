// Golden master ของ API ระบบที่รับมอบ (characterization · ป้าย [E])
// ใช้: node tests/golden/run.mjs [--update]   (Node >= 22.18 · ไม่มี dependency)
//   --update  = ยิงระบบแล้วเขียน tests/golden/*.json ใหม่
//   ไม่ใส่    = ยิงระบบแล้วเทียบกับไฟล์เดิม · ต่าง → พิมพ์เคส+ฟิลด์ที่ต่าง แล้ว exit 1
// BASE_URL ค่าเริ่ม http://localhost:4000
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const BASE = (process.env.BASE_URL || "http://localhost:4000").replace(/\/$/, "");
const DIR = dirname(fileURLToPath(import.meta.url));
const UPDATE = process.argv.includes("--update");
const RESET_NOW = "2026-10-10T10:00:00+07:00";

// บัญชีทดสอบจาก seed (แสดงบนหน้า /login เมื่อ ALLOW_TEST_RESET=1)
const USERS = {
  U01: ["nida@sabai.test", "Nida@2026"], U02: ["ton@sabai.test", "Ton@2026"], U03: ["may@sabai.test", "May@2026"],
  U04: ["fon@sabai.test", "Fon@2026"], U05: ["prae@sabai.test", "Prae@2026"], U06: ["vipa@sabai.test", "Vipa@2026"],
  U07: ["kan@sabai.test", "Kan@2026"], U08: ["liwei@sabai.test", "LiWei@2026"], OWNER: ["owner@sabai.test", "Owner@2026"],
};

// ฟิลด์ที่เปลี่ยนเองทุกรอบ/ขึ้นกับลำดับรัน → ตัดก่อนเทียบ (เหตุผลใน README.md)
const VOLATILE = new Set(["id", "bookingId", "createdAt", "created_at", "updatedAt", "updated_at"]);
function normalize(v) {
  if (Array.isArray(v)) return v.map(normalize);
  if (v && typeof v === "object") {
    const o = {};
    for (const k of Object.keys(v)) if (!VOLATILE.has(k)) o[k] = normalize(v[k]);
    return o;
  }
  return v;
}

async function reset() {
  const r = await fetch(`${BASE}/api/test/reset`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ now: RESET_NOW }) });
  if (r.status !== 200) throw new Error(`reset failed: HTTP ${r.status}`);
}

const cookies = {};
async function login(user) {
  if (!user) return "";
  if (cookies[user]) return cookies[user];
  const [email, password] = USERS[user];
  const r = await fetch(`${BASE}/api/auth/login`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ email, password }) });
  if (r.status !== 200) throw new Error(`login ${user} failed: HTTP ${r.status}`);
  cookies[user] = r.headers.getSetCookie().map((c) => c.split(";")[0]).join("; ");
  return cookies[user];
}

async function call(method, path, { user = null, body } = {}) {
  const headers = { "content-type": "application/json" };
  const ck = await login(user);
  if (ck) headers.cookie = ck;
  const r = await fetch(`${BASE}${path}`, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  const text = await r.text();
  let json;
  try { json = JSON.parse(text); } catch { json = { _text: text }; }
  return { status: r.status, body: normalize(json) };
}

// ── กลุ่ม 1 · POST /api/price ─────────────────────────────────────────────
const D = "2026-10-22";
const S = (o) => ({ type: "single", serviceCode: "S01", date: D, time: "14:00", ...o });
const G = (n, o = {}) => ({ type: "group", serviceCode: "S01", people: n, date: D, time: "14:00", ...o });
const PRICE_CASES = [
  // ผู้ใช้ seed × เดี่ยว S01 ไม่มีตัวเลือกเสริม
  ...[null, "U01", "U02", "U03", "U04", "U05", "U06", "U07", "U08"].map((u) => [`single-S01-${u ?? "guest"}`, u, S({})]),
  // คู่ S02
  ...[null, "U01", "U06"].map((u) => [`couple-S02-${u ?? "guest"}`, u, { type: "couple", serviceCode: "S02", people: 2, date: D, time: "14:00" }]),
  // กลุ่ม 3–6
  ...[3, 4, 5, 6].map((n) => [`group${n}-S01-guest`, null, G(n)]),
  ["group4-S01-U01", "U01", G(4)],
  ["group4-S01-U06", "U06", G(4)],
  ["group3-S01-U07", "U07", G(3)],
  // แพ็กเกจ P01 (รวมรถ)
  ["package1-P01-guest", null, { type: "package", serviceCode: "P01", people: 1, date: D, time: "13:00" }],
  ["package2-P01-guest", null, { type: "package", serviceCode: "P01", people: 2, date: D, time: "13:00" }],
  ["package1-P01-U02", "U02", { type: "package", serviceCode: "P01", people: 1, date: D, time: "13:00" }],
  ["package6-P01-guest-H04", null, { type: "package", serviceCode: "P01", people: 6, date: D, time: "13:00", hotelCode: "H04" }],
  ["package5-P01-guest-H05", null, { type: "package", serviceCode: "P01", people: 5, date: D, time: "13:00", hotelCode: "H05" }],
  // คอร์ส K01 (ผู้มีคอร์ส)
  ["course-K01-U01", "U01", { type: "course", serviceCode: "K01", date: D, time: "14:00" }],
  ["course-K01-U07-1015", "U07", { type: "course", serviceCode: "K01", date: "2026-10-15", time: "14:00" }],
  // แลกแต้ม
  ["single-S01-U04-redeem1", "U04", S({ redeemBlocks: 1 })],
  ["single-S01-U04-redeem2", "U04", S({ redeemBlocks: 2 })],
  ["single-S01-U05-redeem1", "U05", S({ redeemBlocks: 1 })],
  ["single-S01-U06-redeem1", "U06", S({ redeemBlocks: 1 })],
  ["group3-S01-U04-redeem2", "U04", G(3, { redeemBlocks: 2 })],
  // Gift Card
  ["single-S01-guest-GC2000", null, S({ giftCardCode: "SABAI-GC-2000" })],
  ["single-S04-guest-GCPART", null, S({ serviceCode: "S04", giftCardCode: "SABAI-GC-PART" })],
  ["single-S01-U06-GCPART", "U06", S({ giftCardCode: "SABAI-GC-PART" })],
  ["single-S01-U02-GCLAST", "U02", S({ giftCardCode: "SABAI-GC-LAST" })],
  ["single-S01-guest-GCZERO", null, S({ giftCardCode: "SABAI-GC-ZERO" })],
  ["single-S01-guest-GCEXP", null, S({ giftCardCode: "SABAI-GC-EXP" })],
  // รถรับส่ง (ไม่ใช้ H01 H04 H05)
  ["single-S01-guest-H01", null, S({ hotelCode: "H01" })],
  ["single-S01-guest-H04", null, S({ hotelCode: "H04" })],
  ["single-S01-guest-H05", null, S({ hotelCode: "H05" })],
  ["group4-S01-guest-H01", null, G(4, { hotelCode: "H01" })],
  ["group5-S01-guest-H04", null, G(5, { hotelCode: "H04" })],
  ["group6-S01-guest-H05", null, G(6, { hotelCode: "H05" })],
  ["couple-S02-U01-H04", "U01", { type: "couple", serviceCode: "S02", people: 2, date: D, time: "14:00", hotelCode: "H04" }],
  ["single-S01-U08-H05", "U08", S({ hotelCode: "H05" })],
  // วันเกิด + ผสม
  ["single-S01-U02-birthday", "U02", S({ useBirthday: true })],
  ["single-S01-U04-redeem1-H04-GC2000", "U04", S({ redeemBlocks: 1, hotelCode: "H04", giftCardCode: "SABAI-GC-2000" })],
  ["group5-S01-U06-redeem1-H04-GCPART", "U06", G(5, { redeemBlocks: 1, hotelCode: "H04", giftCardCode: "SABAI-GC-PART" })],
  ["group6-S03-U07-H04", "U07", G(6, { serviceCode: "S03", hotelCode: "H04" })],
  ["single-S07-U05-GC2000", "U05", S({ serviceCode: "S07", giftCardCode: "SABAI-GC-2000" })],
];

const GROUPS = [
  {
    file: "price.json",
    run: async () => {
      await reset();
      const out = [];
      for (const [name, user, body] of PRICE_CASES) out.push({ name, user: user ?? "guest", request: { method: "POST", path: "/api/price", body }, ...(await call("POST", "/api/price", { user, body })) });
      return out;
    },
  },
  {
    file: "slots.json",
    run: async () => {
      await reset();
      const out = [];
      for (const svc of ["S01", "S02", "P01"]) for (const date of ["2026-10-22", "2026-10-24"]) {
        const type = svc === "P01" ? "package" : "single";
        const path = `/api/slots?service=${svc}&date=${date}&type=${type}&people=1`;
        out.push({ name: `slots-${svc}-${date}`, user: "guest", request: { method: "GET", path }, ...(await call("GET", path)) });
      }
      return out;
    },
  },
  {
    file: "admin-queue.json",
    run: async () => {
      await reset();
      const out = [];
      for (let d = 12; d <= 17; d++) {
        const path = `/api/admin/bookings?date=2026-10-${d}`;
        out.push({ name: `queue-2026-10-${d}`, user: "OWNER", request: { method: "GET", path }, ...(await call("GET", path, { user: "OWNER" })) });
      }
      return out;
    },
  },
];

function diff(a, b, path, acc) {
  if (acc.length >= 15) return acc;
  if (typeof a !== typeof b || Array.isArray(a) !== Array.isArray(b) || a === null || b === null || typeof a !== "object") {
    if (JSON.stringify(a) !== JSON.stringify(b)) acc.push(`${path || "(root)"}: golden=${JSON.stringify(a)} actual=${JSON.stringify(b)}`);
    return acc;
  }
  const keys = new Set([...Object.keys(a), ...Object.keys(b)]);
  for (const k of keys) diff(a[k], b[k], Array.isArray(a) ? `${path}[${k}]` : path ? `${path}.${k}` : k, acc);
  return acc;
}

let failed = 0, total = 0;
for (const g of GROUPS) {
  const cases = await g.run();
  total += cases.length;
  const file = join(DIR, g.file);
  if (UPDATE) {
    writeFileSync(file, JSON.stringify({ group: g.file.replace(".json", ""), resetNow: RESET_NOW, cases }, null, 2) + "\n");
    console.log(`updated ${g.file}: ${cases.length} cases`);
    continue;
  }
  if (!existsSync(file)) { console.log(`MISSING ${g.file} (run with --update first)`); failed++; continue; }
  const golden = JSON.parse(readFileSync(file, "utf8")).cases;
  const byName = new Map(golden.map((c) => [c.name, c]));
  let gf = 0;
  for (const c of cases) {
    const exp = byName.get(c.name);
    if (!exp) { console.log(`  NEW  ${g.file} ${c.name} (not in golden)`); gf++; continue; }
    const d = diff({ status: exp.status, body: exp.body }, { status: c.status, body: c.body }, "", []);
    if (d.length) { gf++; console.log(`  DIFF ${g.file} ${c.name}`); for (const line of d) console.log(`       ${line}`); }
  }
  for (const n of byName.keys()) if (!cases.find((c) => c.name === n)) { console.log(`  GONE ${g.file} ${n}`); gf++; }
  failed += gf;
  console.log(`${gf ? "FAIL" : "ok  "} ${g.file}: ${cases.length - gf}/${cases.length} cases match`);
}
if (!UPDATE) {
  console.log(failed ? `GOLDEN FAIL: ${failed} case(s) differ of ${total}` : `GOLDEN PASS: ${total}/${total}`);
  process.exit(failed ? 1 : 0);
}
