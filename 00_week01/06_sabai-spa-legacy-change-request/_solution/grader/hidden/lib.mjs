// hidden test helpers (รันใน node:22-alpine ใน docker network ของเครื่องตรวจ)
//   env: BASE_URL · VARIANT_JSON (ค่ารายคนจาก variants.json) · LEARNER (โฟลเดอร์ HEAD ของผู้สอบ ถ้า mount)
export const BASE = (process.env.BASE_URL || "http://localhost:4000").replace(/\/$/, "");
export const V = JSON.parse(process.env.VARIANT_JSON || "{}");
export const SEED_NOW = "2026-10-10T10:00:00+07:00";

export const USERS = {
  U01: ["nida@sabai.test", "Nida@2026"], U02: ["ton@sabai.test", "Ton@2026"], U03: ["may@sabai.test", "May@2026"],
  U04: ["fon@sabai.test", "Fon@2026"], U05: ["prae@sabai.test", "Prae@2026"], U06: ["vipa@sabai.test", "Vipa@2026"],
  U07: ["kan@sabai.test", "Kan@2026"], U08: ["liwei@sabai.test", "LiWei@2026"], OWNER: ["owner@sabai.test", "Owner@2026"],
};
export const GUEST = { contactName: "เครื่องตรวจ", contactPhone: "0899999999" };

export class Client {
  constructor(lang = "th") { this.cookie = ""; this.lang = lang; }
  async req(method, path, body) {
    const headers = { "Content-Type": "application/json", "Accept-Language": this.lang };
    const ck = [this.cookie, `lang=${this.lang}`].filter(Boolean).join("; ");
    headers.Cookie = ck;
    const r = await fetch(BASE + path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body), signal: AbortSignal.timeout(30000) });
    const set = r.headers.get("set-cookie");
    if (set) { const m = set.match(/sabai_session=([^;]*)/); if (m) this.cookie = `sabai_session=${m[1]}`; }
    const text = await r.text();
    let json; try { json = JSON.parse(text); } catch { json = { raw: text.slice(0, 300) }; }
    return { status: r.status, json: json ?? {}, text };
  }
  get(p) { return this.req("GET", p); }
  post(p, b = {}) { return this.req("POST", p, b); }
  async html(path) {
    const r = await fetch(BASE + path, { headers: { Cookie: [this.cookie, `lang=${this.lang}`].filter(Boolean).join("; "), "Accept-Language": this.lang }, signal: AbortSignal.timeout(30000) });
    return (await r.text()).replace(/<!--[\s\S]*?-->/g, "");
  }
}
export const guest = (lang = "th") => new Client(lang);
export async function login(u, lang = "th") {
  const c = new Client(lang);
  const [email, password] = USERS[u];
  const r = await c.post("/api/auth/login", { email, password });
  if (r.status !== 200) throw new Error(`login ${u} → ${r.status}`);
  return c;
}
export async function reset(now = SEED_NOW) {
  const r = await guest().post("/api/test/reset", { now });
  if (r.status !== 200) throw new Error(`reset → ${r.status} ${JSON.stringify(r.json).slice(0, 200)}`);
  return r.json;
}
export async function me(u) {
  const j = (await (await login(u)).get("/api/me")).json;
  return { points: j.points, lifetimeSpend: j.lifetimeSpend, tier: j.tier };
}
/** ราคา → จองด้วย quotedTotal เดียวกัน */
export async function book(c, body) {
  const q = await c.post("/api/price", body);
  if (q.status !== 200) return q;
  return c.post("/api/bookings", { ...GUEST, ...body, quotedTotal: q.json.total });
}
export const near = (a, b) => typeof a === "number" && Math.abs(a - b) < 0.001;
export const j = (x) => JSON.stringify(x);

/** ตัวเก็บคะแนน: check(id, label, weight, fn) · fn คืน true หรือ string (เหตุผลที่ไม่ผ่าน) / throw = ไม่ผ่าน */
export class Score {
  constructor(item, part) { this.item = item; this.part = part; this.checks = []; }
  async check(id, label, weight, fn) {
    let ok = false, detail = "";
    try {
      const r = await fn();
      ok = r === true;
      if (!ok) detail = typeof r === "string" ? r : j(r);
    } catch (e) { detail = "exception: " + (e?.message ?? e); }
    this.checks.push({ id, label, weight, ok, detail: detail.slice(0, 400) });
    console.log(`${ok ? "PASS" : "FAIL"} [${weight}] ${id} ${label}${ok ? "" : " :: " + detail.slice(0, 300)}`);
  }
  done() {
    const score = this.checks.reduce((a, c) => a + (c.ok ? c.weight : 0), 0);
    const max = this.checks.reduce((a, c) => a + c.weight, 0);
    console.log("RESULT " + JSON.stringify({ item: this.item, part: this.part, score: Math.round(score * 1000) / 1000, max, checks: this.checks }));
  }
}
/** ผลที่คาดไม่ตรง → คืนข้อความ (ใช้ใน check) */
export function expectEq(actual, expected, label = "") {
  const ok = typeof expected === "number" && typeof actual === "number" ? Math.abs(actual - expected) < 0.001 : j(actual) === j(expected);
  return ok ? true : `${label} ได้ ${j(actual)} ควรเป็น ${j(expected)}`;
}
export function all(...rs) {
  const bad = rs.filter((r) => r !== true);
  return bad.length ? bad.join(" · ") : true;
}
