// EX7 (ชุด A) เทสต์ของผู้สอบ: GET /api/me/points
const BASE = (process.env.BASE_URL || "http://localhost:4000").replace(/\/$/, "");
const call = async (method, p, b, ck) => {
  const r = await fetch(BASE + p, { method, headers: { "Content-Type": "application/json", ...(ck ? { Cookie: ck } : {}) }, body: b === undefined ? undefined : JSON.stringify(b) });
  return { status: r.status, set: r.headers.get("set-cookie"), json: await r.json().catch(() => ({})) };
};
await call("POST", "/api/test/reset", {});
const l = await call("POST", "/api/auth/login", { email: "nida@sabai.test", password: "Nida@2026" });
const ck = l.set.match(/sabai_session=[^;]*/)[0];
const h = await call("GET", "/api/me/points", undefined, ck);
const anon = await call("GET", "/api/me/points");
const fails = [];
if (h.status !== 200 || h.json.balance !== 99) fails.push(`U01 balance ${h.json.balance}`);
const it = h.json.items ?? [];
if (it.length !== 2 || it[0].reason !== "earn" || it[0].points !== 19 || it[0].balanceAfter !== 99 || it[1].reason !== "opening" || it[1].balanceAfter !== 80) fails.push("U01 items " + JSON.stringify(it));
if (anon.status !== 401) fails.push(`anon ${anon.status}`);
console.log(fails.length ? "FAIL " + fails.join(" | ") : "PASS points history API");
process.exit(fails.length ? 1 : 0);
