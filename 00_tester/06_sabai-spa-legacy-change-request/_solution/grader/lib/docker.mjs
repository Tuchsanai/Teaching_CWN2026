// ระบบที่ทดสอบ (SUT) = postgres:16-alpine + image เว็บ อยู่ใน docker network ของผู้สอบแต่ละคน · ไม่ใช้พอร์ต host
import { readFileSync, mkdirSync, existsSync } from "node:fs";
import { sh, sleep } from "./sh.mjs";

export const IMG = {
  pg: "postgres:16-alpine",
  node: "node:22-alpine",
  pw: "mcr.microsoft.com/playwright:v1.63.0-noble",
};
const dk = (args, o) => sh("docker", args, o);
const fwd = (p) => p.replace(/\\/g, "/");

export async function imageExists(tag) {
  return (await dk(["image", "inspect", "--format", "{{.Id}}", tag])).code === 0;
}
const building = new Map();
/** build image เว็บ (context = web/ · build-context dbinit = db/init) ถ้ายังไม่มี tag นี้ */
export function ensureImage(tag, webDir, initDir, log) {
  if (building.has(tag)) return building.get(tag);
  const p = (async () => {
    if (await imageExists(tag)) { log?.(`image ${tag} มีแล้ว (ใช้ซ้ำ)`); return { ok: true, cached: true, ms: 0 }; }
    log?.(`build ${tag} …`);
    const r = await dk(["build", "-q", "--build-context", `dbinit=${fwd(initDir)}`, "-t", tag, fwd(webDir)], { timeoutMs: 15 * 60_000 });
    log?.(`build ${tag} → exit ${r.code} (${Math.round(r.ms / 1000)} วินาที)`);
    return { ok: r.code === 0, cached: false, ms: r.ms, err: r.code === 0 ? "" : (r.err || r.out).slice(-3000) };
  })();
  building.set(tag, p);
  return p;
}

export async function ensureNetwork(net) {
  if ((await dk(["network", "inspect", net])).code !== 0) await dk(["network", "create", net]);
}

export class Sut {
  constructor(ctx, lane) {
    this.ctx = ctx;
    this.lane = lane;
    this.db = `${ctx.prefix}-${ctx.id}-${lane}-db`;
    this.web = `${ctx.prefix}-${ctx.id}-${lane}-web`;
    this.net = ctx.net;
    this.url = `http://${this.web}:3000`;
  }
  log(m) { this.ctx.log(`[${this.lane}] ${m}`); }
  async startDb(initDir) {
    await dk(["rm", "-f", this.web, this.db]);
    const r = await dk(["run", "-d", "--name", this.db, "--network", this.net, "--label", `sabai-grader=${this.ctx.prefix}`,
      "-e", "POSTGRES_USER=sabai", "-e", "POSTGRES_PASSWORD=sabai", "-e", "POSTGRES_DB=sabai", "-e", "TZ=Asia/Bangkok", "-e", "PGTZ=Asia/Bangkok",
      "-v", `${fwd(initDir)}:/docker-entrypoint-initdb.d:ro`, IMG.pg]);
    if (r.code !== 0) throw new Error(`start db: ${r.err}`);
    // TCP พร้อม = init เสร็จแล้ว (ระหว่าง init postgres ฟังแค่ unix socket)
    for (let i = 0; i < 120; i++) {
      await sleep(1000);
      const st = await dk(["inspect", "-f", "{{.State.Running}}", this.db]);
      if (st.out.trim() !== "true") {
        const lg = await dk(["logs", "--tail", "30", this.db]);
        throw new Error(`db หยุดระหว่าง init (db/init มี error?): ${(lg.err + lg.out).slice(-1500)}`);
      }
      const ok = await dk(["exec", this.db, "pg_isready", "-h", "127.0.0.1", "-U", "sabai", "-d", "sabai"]);
      if (ok.code === 0) {
        const t = await this.sql("select 1 from app_setting limit 1");
        if (t.code === 0) { this.log("db พร้อม"); return; }
      }
    }
    throw new Error("db ไม่พร้อมใน 120 วินาที");
  }
  async startWeb(image) {
    await dk(["rm", "-f", this.web]);
    const r = await dk(["run", "-d", "--name", this.web, "--network", this.net, "--label", `sabai-grader=${this.ctx.prefix}`,
      "-e", `DATABASE_URL=postgres://sabai:sabai@${this.db}:5432/sabai`, "-e", "HOSTNAME=0.0.0.0", "-e", "TZ=Asia/Bangkok",
      "-e", "ALLOW_TEST_RESET=1", "-e", "SESSION_SECRET=sabai-grader-secret", image]);
    if (r.code !== 0) throw new Error(`start web: ${r.err}`);
    const probe = "fetch('http://127.0.0.1:3000/api/health').then(r=>r.json()).then(j=>process.exit(j.db?0:1)).catch(()=>process.exit(1))";
    for (let i = 0; i < 90; i++) {
      await sleep(1000);
      const ok = await dk(["exec", this.web, "node", "-e", probe]);
      if (ok.code === 0) { this.log(`web พร้อม (${image})`); return; }
      const st = await dk(["inspect", "-f", "{{.State.Running}}", this.web]);
      if (st.out.trim() !== "true") break;
    }
    const lg = await dk(["logs", "--tail", "40", this.web]);
    throw new Error(`web ไม่พร้อม: ${(lg.err + lg.out).slice(-1500)}`);
  }
  async start(image, initDir) { await this.startDb(initDir); await this.startWeb(image); }
  sql(q) { return dk(["exec", this.db, "psql", "-U", "sabai", "-d", "sabai", "-tA", "-v", "ON_ERROR_STOP=1", "-c", q]); }
  sqlFile(content) { return dk(["exec", "-i", this.db, "psql", "-U", "sabai", "-d", "sabai", "-v", "ON_ERROR_STOP=1", "-f", "-"], { input: content, timeoutMs: 120_000 }); }
  async counts() {
    const r = await this.sql("select (select count(*) from customer)||'|'||(select count(*) from booking)||'|'||(select count(*) from point_txn)");
    const [customer, booking, pointTxn] = r.out.trim().split("|").map(Number);
    return { customer, booking, pointTxn };
  }
  async stop() { await dk(["rm", "-f", this.web, this.db]); }

  /** node:22-alpine ใน network เดียวกัน · mounts = [[hostDir, containerDir, ro?]] */
  async node(script, { mounts = [], cwd = "/w", env = {}, args = [], timeoutMs = 10 * 60_000, tag = "n" } = {}) {
    const name = `${this.ctx.prefix}-${this.ctx.id}-${this.lane}-${tag}-${Math.random().toString(36).slice(2, 7)}`;
    const a = ["run", "--rm", "--name", name, "--network", this.net, "--label", `sabai-grader=${this.ctx.prefix}`, "-w", cwd, "-e", `BASE_URL=${this.url}`];
    for (const [k, v] of Object.entries(env)) a.push("-e", `${k}=${v}`);
    for (const [h, c, ro] of mounts) a.push("-v", `${fwd(h)}:${c}${ro ? ":ro" : ""}`);
    a.push(IMG.node, "node", script, ...args);
    return dk(a, { timeoutMs, killName: name });
  }
  /** Playwright 1.63 ใน network เดียวกัน · e2eDir = โฟลเดอร์ที่มี playwright.config.ts */
  async playwright(e2eDir, nmDir, pwArgs, { env = {}, timeoutMs = 30 * 60_000, tag = "pw", jsonOut } = {}) {
    const name = `${this.ctx.prefix}-${this.ctx.id}-${this.lane}-${tag}-${Math.random().toString(36).slice(2, 7)}`;
    if (jsonOut) mkdirSync(`${e2eDir}/out`, { recursive: true });
    const a = ["run", "--rm", "--name", name, "--network", this.net, "--ipc=host", "--label", `sabai-grader=${this.ctx.prefix}`,
      "-v", `${fwd(e2eDir)}:/e`, "-v", `${fwd(nmDir)}:/e/node_modules`, "-w", "/e", "-e", `BASE_URL=${this.url}`, "-e", "CI=1"];
    if (jsonOut) a.push("-e", `PLAYWRIGHT_JSON_OUTPUT_NAME=/e/out/${jsonOut}`);
    for (const [k, v] of Object.entries(env)) a.push("-e", `${k}=${v}`);
    a.push(IMG.pw, "npx", "playwright", "test", ...pwArgs);
    const r = await dk(a, { timeoutMs, killName: name });
    let report = null;
    if (jsonOut && existsSync(`${e2eDir}/out/${jsonOut}`)) {
      try { report = JSON.parse(readFileSync(`${e2eDir}/out/${jsonOut}`, "utf8")); } catch { /* ignore */ }
    }
    return { ...r, report };
  }
}

/** สรุปผล Playwright JSON → passed (แบบ list reporter: รวม expected-fail) · expectedFail · failed · flaky · skipped */
export function pwSummary(report) {
  const tests = [];
  const walk = (suite, path) => {
    for (const s of suite.suites ?? []) walk(s, [...path, s.title]);
    for (const spec of suite.specs ?? []) {
      for (const t of spec.tests ?? []) {
        const last = (t.results ?? []).at(-1);
        tests.push({ title: spec.title, file: spec.file, project: t.projectName, status: t.status, expectedStatus: t.expectedStatus, result: last?.status, error: (last?.error?.message ?? "").replace(/\u001b\[[0-9;]*m/g, "").slice(0, 300) });
      }
    }
  };
  if (report) for (const s of report.suites ?? []) walk(s, [s.title]);
  const sum = { passed: 0, expectedFail: 0, failed: 0, flaky: 0, skipped: 0, total: tests.length, failedTitles: [] };
  for (const t of tests) {
    if (t.status === "skipped") sum.skipped++;
    else if (t.status === "expected") { sum.passed++; if (t.expectedStatus === "failed") sum.expectedFail++; }
    else if (t.status === "flaky") sum.flaky++;
    else { sum.failed++; sum.failedTitles.push(`${t.project}: ${t.title}`); }
  }
  return { sum, tests };
}

export async function cleanupPrefix(prefix, { images = false } = {}) {
  const ps = await dk(["ps", "-aq", "--filter", `label=sabai-grader=${prefix}`]);
  const ids = ps.out.split("\n").filter(Boolean);
  if (ids.length) await dk(["rm", "-f", ...ids]);
  const nets = await dk(["network", "ls", "--format", "{{.Name}}"]);
  for (const n of nets.out.split("\n").filter((x) => x.startsWith(prefix + "-"))) await dk(["network", "rm", n]);
  if (images) {
    const im = await dk(["images", "--format", "{{.Repository}}:{{.Tag}}"]);
    const tags = im.out.split("\n").filter((x) => x.startsWith(prefix + "-") || x.startsWith(prefix + "/"));
    if (tags.length) await dk(["rmi", "-f", ...tags]);
    return { containers: ids.length, images: tags.length };
  }
  return { containers: ids.length };
}
