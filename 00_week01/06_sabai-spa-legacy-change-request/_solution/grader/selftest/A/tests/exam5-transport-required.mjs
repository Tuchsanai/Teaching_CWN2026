// EX5-red (ชุด A): ทำซ้ำเรื่องร้องเรียน — ติ๊กรถแต่ไม่มีโรงแรม/ระยะ ต้องถูกปฏิเสธ 422 TRANSPORT_DISTANCE_REQUIRED
const BASE = (process.env.BASE_URL || "http://localhost:4000").replace(/\/$/, "");
const post = (p, b) => fetch(BASE + p, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(b ?? {}) });
await post("/api/test/reset", {});
const body = { type: "single", serviceCode: "S01", date: "2026-10-20", time: "10:00", wantTransport: true, contactName: "t", contactPhone: "0811111111" };
const p = await post("/api/price", body);
const pj = await p.json();
const b = await post("/api/bookings", { ...body, quotedTotal: 1000 });
const bj = await b.json();
await post("/api/test/reset", {});
const ok = p.status === 422 && pj.error === "TRANSPORT_DISTANCE_REQUIRED" && b.status === 422 && bj.error === "TRANSPORT_DISTANCE_REQUIRED";
console.log(ok ? "PASS" : `FAIL: price ${p.status} ${pj.error ?? ""} · bookings ${b.status} ${bj.error ?? ""}`);
process.exit(ok ? 0 : 1);
