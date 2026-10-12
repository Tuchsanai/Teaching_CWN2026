// smoke test วันขึ้นระบบจริง (ชุด A) · อ่านอย่างเดียว · ไม่ reset · ไม่สร้างข้อมูล
//   node tests/smoke.mjs   (BASE_URL ค่าเริ่ม http://localhost:4000)
import { readFileSync } from "node:fs";
const BASE = (process.env.BASE_URL || "http://localhost:4000").replace(/\/$/, "");
let V = { freeKm: 7, feePerVehicle: 350 };
try { V = JSON.parse(readFileSync(new URL("../exam/VARIANT.json", import.meta.url), "utf8")); } catch { /* ใช้ค่าเริ่ม */ }
const get = (p) => fetch(BASE + p).then(async (r) => ({ status: r.status, json: await r.json().catch(() => ({})) }));
const post = (p, b) => fetch(BASE + p, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(b) }).then(async (r) => ({ status: r.status, json: await r.json().catch(() => ({})) }));
const checks = [
  ["ระบบขึ้น", async () => (await get("/api/health")).json.db === true],
  ["ข้อ 4 ค่ารถ H04", async () => (await get("/api/transport?hotel=H04&people=1")).json.fee === V.feePerVehicle],
  ["ข้อ 5 ติ๊กรถไม่มีระยะ → 422", async () => (await post("/api/price", { type: "single", serviceCode: "S01", date: "2026-10-20", time: "10:00", wantTransport: true })).json.error === "TRANSPORT_DISTANCE_REQUIRED"],
  ["ข้อ 6 S03 ไม่อยู่ในรายการบริการ", async () => !((await get("/api/services")).json.services ?? []).some((s) => s.code === "S03")],
  ["ข้อ 7 /api/me/points ต้องล็อกอิน", async () => (await get("/api/me/points")).status === 401],
];
let bad = 0;
for (const [name, fn] of checks) {
  let ok = false;
  try { ok = await fn(); } catch { ok = false; }
  if (!ok) bad++;
  console.log(`${ok ? "✅" : "❌"} ${name}`);
}
process.exit(bad ? 1 : 0);
