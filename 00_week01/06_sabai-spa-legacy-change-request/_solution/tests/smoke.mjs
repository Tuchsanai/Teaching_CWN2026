// smoke test วันขึ้นระบบจริง (CR-01–05) — อ่านอย่างเดียว: ไม่ reset · ไม่สร้าง/แก้ข้อมูล · ไม่ล็อกอิน
//   ใช้ (PowerShell จากโฟลเดอร์บท): node tests/smoke.mjs        (ค่าเริ่ม BASE_URL=http://localhost:4000)
//   พอร์ตอื่น: $env:BASE_URL="http://localhost:<พอร์ต>"; node tests/smoke.mjs
//   exit 0 = ผ่านทุกข้อ · exit 1 = มีข้อไม่ผ่าน (รวมกรณีเว็บล่ม/ต่อไม่ติด)
//   Node >= 22.18 · ไม่มี dependency
//   ข้อ 6 ยิง POST แบบไม่ล็อกอิน: ระบบตอบ 401 ก่อนอ่าน body/แตะฐาน (web/lib/server/booking.ts rescheduleBooking บรรทัดแรก) จึงไม่เปลี่ยนข้อมูล

const BASE = (process.env.BASE_URL || "http://localhost:4000").replace(/\/$/, "");
const TIMEOUT_MS = 10_000;
// วันหยุดที่ร้านแจ้งใน CR-04 [D:CR-04]
const SHOP_HOLIDAYS = ["2026-10-23", "2026-12-05", "2026-12-31"];

async function hit(method, path, body) {
  const r = await fetch(BASE + path, {
    method,
    headers: body === undefined ? {} : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
    redirect: "manual",
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });
  const text = await r.text();
  let json = null;
  try {
    json = JSON.parse(text);
  } catch {}
  return { status: r.status, json };
}

const checks = [
  ["1 health db:true", async () => {
    const r = await hit("GET", "/api/health");
    return [r.status === 200 && r.json?.db === true, `${r.status} db=${r.json?.db}`];
  }],
  ["2 GET /api/services 200", async () => {
    const r = await hit("GET", "/api/services");
    return [r.status === 200, `${r.status}`];
  }],
  ["3 /api/holidays มีวันหยุดที่ร้านแจ้ง (CR-04)", async () => {
    const r = await hit("GET", "/api/holidays");
    const dates = (r.json?.holidays || []).map((h) => h.date);
    const missing = SHOP_HOLIDAYS.filter((d) => !dates.includes(d));
    return [r.status === 200 && missing.length === 0, `${r.status} พบ ${dates.length} วัน${missing.length ? ` ขาด ${missing.join(",")}` : ""}`];
  }],
  ["4 หน้า /book 200", async () => {
    const r = await hit("GET", "/book");
    return [r.status === 200, `${r.status}`];
  }],
  ["5 CR-01 GET reschedule-slots ไม่ล็อกอิน = 401", async () => {
    const r = await hit("GET", "/api/bookings/1/reschedule-slots?date=2026-10-21");
    return [r.status === 401, `${r.status}${r.status === 404 ? " (ไม่มี endpoint)" : ""}`];
  }],
  ["6 CR-01 POST reschedule ไม่ล็อกอิน = 401", async () => {
    const r = await hit("POST", "/api/bookings/1/reschedule", {});
    return [r.status === 401, `${r.status}${r.status === 404 ? " (ไม่มี endpoint)" : ""}`];
  }],
  ["7 CR-05 GET /api/admin/report ไม่ล็อกอิน = 401", async () => {
    const r = await hit("GET", "/api/admin/report?from=2026-09-01&to=2026-09-30");
    return [r.status === 401, `${r.status}${r.status === 404 ? " (ไม่มี endpoint)" : ""}`];
  }],
];

console.log(`smoke ${BASE}`);
console.log("| ข้อ | ผล | รายละเอียด |");
console.log("|---|---|---|");
let fail = 0;
for (const [name, fn] of checks) {
  let ok = false;
  let detail = "";
  try {
    [ok, detail] = await fn();
  } catch (e) {
    detail = `ต่อไม่ติด: ${e.cause?.code || e.name || e.message}`;
  }
  if (!ok) fail++;
  console.log(`| ${name} | ${ok ? "ผ่าน" : "ไม่ผ่าน"} | ${detail} |`);
}
console.log(`สรุป ${checks.length - fail}/${checks.length} ผ่าน`);
process.exit(fail ? 1 : 0);
