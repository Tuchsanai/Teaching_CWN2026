// Real browser test of the deployed app: real Chromium, the real page served by the app,
// real API calls to real models (no mocks, no route stubs).
//   node tests/e2e/chat_e2e.js
// URL comes from .env APP_TEST_URL; the token is read from the owner-only token file and typed
// into the password field only — it is never printed, logged, or written to the artifacts.
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const PW = process.env.PLAYWRIGHT_CORE || "/usr/lib/node_modules/@playwright/cli/node_modules/playwright-core";
const { chromium } = require(PW);
const env = Object.fromEntries(fs.readFileSync(path.join(ROOT, ".env"), "utf8").split("\n")
  .filter((l) => l.includes("=")).map((l) => [l.slice(0, l.indexOf("=")), l.slice(l.indexOf("=") + 1)]));
const BASE = (env.APP_TEST_URL || "").replace(/\/+$/, "");
const TOKEN = fs.readFileSync(path.join(ROOT, env.API_TOKEN_FILE || "secrets/api_token"), "utf8").trim();
const OUT = path.join(ROOT, "tests", "artifacts");
fs.mkdirSync(OUT, { recursive: true });
const ROUND_TIMEOUT = 300000;   // backend CLI timeout is 240 s

const logLines = [];
function log(line) {
  const safe = String(line).split(TOKEN).join("[REDACTED_API_TOKEN]");
  logLines.push(`${new Date().toISOString()} ${safe}`);
  console.log(safe);
}
const results = [];
function check(name, cond, detail = "") { results.push(!!cond); log(`${cond ? "PASS" : "FAIL"} | ${name}${detail ? " | " + detail : ""}`); }

const ROUNDS = [
  // Fable 5 rounds
  { select: { provider: "claude", model: "fable", effort: "low", account: "yolo1" },
    text: "สวัสดีครับ ผมชื่อนนท์ มีแมวชื่อส้มโอ ช่วยจำไว้ด้วย ตอบสั้น ๆ หนึ่งประโยค", expect: [] },
  { text: "ผมชอบเลข 7 และชอบสีฟ้า จำไว้ด้วยนะ ตอบสั้น ๆ ว่ารับทราบ", expect: [] },
  { text: "แมวของผมชื่ออะไร ตอบแค่ชื่อ", expect: [["ส้มโอ", "Som-O", "Som O", "Somo"]] },
  { text: "เลขที่ผมชอบคูณ 6 ได้เท่าไร ตอบเป็นตัวเลขอย่างเดียว", expect: [["42", "๔๒"]] },
  { text: "สรุปสิ่งที่คุณรู้เกี่ยวกับผมในหนึ่งประโยคสั้น ๆ", expect: [["นนท์"], ["ส้มโอ"]] },
  // switch to Codex gpt-6-astra, same conversation, 5 rounds
  { select: { provider: "codex", model: "gpt-6-astra", effort: "low", account: "cyolo1" },
    text: "ผมชื่ออะไร ตอบแค่ชื่อ", expect: [["นนท์"]] },
  { text: "สีที่ผมชอบคือสีอะไร ตอบคำเดียว", expect: [["ฟ้า", "blue"]] },
  { text: "ก่อนหน้านี้ผมถามว่าเลขที่ชอบคูณ 6 ได้เท่าไร คำตอบคืออะไร ตอบเป็นตัวเลขอย่างเดียว", expect: [["42", "๔๒"]] },
  { text: "ผมย้ายไปอยู่เชียงใหม่แล้ว จำไว้ด้วย ตอบสั้น ๆ ว่ารับทราบ", expect: [] },
  { text: "สรุปข้อมูลทั้งหมดเกี่ยวกับผมและแมวในหนึ่งประโยค", expect: [["นนท์"], ["ส้มโอ"], ["เชียงใหม่", "Chiang Mai"]] },
];
const SHOT_AFTER = { 3: "01-rounds-1-3-fable", 5: "02-rounds-4-5-fable", 8: "03-rounds-6-8-astra", 10: "04-rounds-9-10-astra" };

(async () => {
  if (!BASE) throw new Error("APP_TEST_URL is empty in .env (run scripts/deploy.sh first)");
  const origin = new URL(BASE).origin;
  log(`test URL (from devtools): ${BASE}/   user URL: ${env.APP_URL || "(not set)"}`);
  const browser = await chromium.launch();
  log(`browser: Chromium ${browser.version()}`);
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 }, acceptDownloads: true, colorScheme: "light" });
  const page = await ctx.newPage();
  const requests = [];
  const chatPosts = [];
  page.on("request", (r) => {
    requests.push(r.url());
    if (r.url().endsWith("/v1/chat/completions") && r.method() === "POST") chatPosts.push(JSON.parse(r.postData()));
  });
  page.on("pageerror", (e) => check("no page errors", false, e.message));

  await page.goto(BASE + "/", { waitUntil: "load" });
  check("page served by the app", (await page.title()) === "Multi-Account Chat");
  check("API URL field defaults to the page origin", (await page.inputValue("#apiUrl")) === origin, await page.inputValue("#apiUrl"));
  await page.waitForFunction(() => document.querySelector("#chipServer").dataset.state === "ok", null, { timeout: 20000 });
  check("status 1: server answers /health", true);
  check("token field is a password field", (await page.getAttribute("#token", "type")) === "password");

  await page.fill("#token", TOKEN);
  await page.click("#connectBtn");
  await page.waitForFunction(() => document.querySelector("#chipToken").dataset.state === "ok", null, { timeout: 30000 });
  check("status 2: token accepted, options loaded", true, await page.textContent("#stepToken .step-detail"));
  check("status 3 not claimed before any answer", (await page.$eval("#chipAccount", (e) => e.dataset.state)) === "unknown");
  const optionList = async (id) => page.$$eval(`#${id} option`, (os) => os.map((o) => o.value));

  const transcript = [];
  for (let i = 0; i < ROUNDS.length; i++) {
    const r = ROUNDS[i], n = i + 1;
    if (r.select) {
      const s = r.select;
      await page.selectOption("#provider", s.provider);
      check(`round ${n}: model options for ${s.provider} come from /v1/models`, (await optionList("model")).includes(s.model), (await optionList("model")).join(","));
      await page.selectOption("#model", s.model);
      check(`round ${n}: effort options for ${s.model}`, (await optionList("effort")).includes(s.effort), (await optionList("effort")).join(","));
      await page.selectOption("#effort", s.effort);
      await page.selectOption("#account", s.account);
      if (n > 1) {
        const warn = await page.isVisible("#recipientWarn");
        check(`round ${n}: warning shown after switching provider/account`, warn, warn ? await page.textContent("#recipientWarnText") : "");
      }
    }
    const chosen = {
      provider: await page.inputValue("#provider"), model: await page.inputValue("#model"),
      effort: await page.inputValue("#effort"), account: await page.inputValue("#account"),
    };
    await page.click("#prompt");
    await page.keyboard.type(r.text);
    const before = await page.$$eval(".msg.assistant:not(.waiting)", (e) => e.length);
    const postsBefore = chatPosts.length;
    const t0 = Date.now();
    await page.click("#sendBtn");
    check(`round ${n}: send disabled while waiting`, await page.isDisabled("#sendBtn"));
    await page.waitForFunction((b) => document.querySelectorAll(".msg.assistant:not(.waiting)").length > b ||
      document.querySelector(".notice.error"), before, { timeout: ROUND_TIMEOUT });
    const secs = ((Date.now() - t0) / 1000).toFixed(1);
    if (await page.$(".notice.error")) {
      check(`round ${n}: got a real answer`, false, (await page.textContent(".notice.error")).slice(0, 200));
      break;
    }
    const sent = chatPosts[postsBefore];
    check(`round ${n}: request uses the selected dropdown values`,
      sent && sent.provider === chosen.provider && sent.model === chosen.model && sent.reasoning_effort === chosen.effort && sent.account === chosen.account,
      JSON.stringify(chosen));
    check(`round ${n}: full history sent`, sent && sent.messages.length === 2 * n - 1, `messages=${sent && sent.messages.length}`);
    const last = page.locator(".msg.assistant:not(.waiting)").last();
    const answer = (await last.locator(".bubble").textContent()).trim();
    const meta = (await last.locator(".meta").textContent()).trim();
    check(`round ${n}: answer meta matches selection`, meta.includes(chosen.model) && meta.includes(chosen.account) && meta.includes(chosen.effort), meta);
    const missing = r.expect.filter((alts) => !alts.some((a) => answer.toLowerCase().includes(a.toLowerCase())));
    check(`round ${n}: answer (${secs}s)` + (r.expect.length ? " recalls earlier context" : ""), answer.length > 0 && missing.length === 0,
      JSON.stringify(answer.slice(0, 160)) + (missing.length ? ` missing ${JSON.stringify(missing)}` : ""));
    transcript.push({ round: n, ...chosen, question: r.text, answer, seconds: Number(secs) });
    if (n === 1 || n === 6) {
      check(`round ${n}: status 3 confirmed for ${chosen.account} after a real answer`, (await page.$eval("#chipAccount", (e) => e.dataset.state)) === "ok");
    }
    if (SHOT_AFTER[n]) {
      await page.$eval("#log", (l) => { l.scrollTop = l.scrollHeight; });
      await page.screenshot({ path: path.join(OUT, `${SHOT_AFTER[n]}-1440x1000.png`) });
      log(`screenshot: tests/artifacts/${SHOT_AFTER[n]}-1440x1000.png`);
    }
  }

  // screenshots clipped to the real message elements of 2-3 rounds each (actual UI, nothing redrawn)
  const groups = [[1, 3], [4, 5], [6, 8], [9, 10]];
  for (const [a, b] of groups) {
    if (transcript.length < b) break;
    const clip = await page.evaluate(([i, j]) => {
      const all = document.querySelectorAll("#logInner .msg");
      all[i].scrollIntoView({ block: "start" });
      const log = document.querySelector("#log").getBoundingClientRect();
      const top = Math.max(log.top, all[i].getBoundingClientRect().top - 10);
      const bottom = Math.min(log.bottom, all[j].getBoundingClientRect().bottom + 10);
      return { x: Math.round(log.left), y: Math.round(top), width: Math.round(log.width), height: Math.round(bottom - top),
               fits: all[j].getBoundingClientRect().bottom <= log.bottom };
    }, [(a - 1) * 2, b * 2 - 1]);
    const { fits, ...box } = clip;
    await page.screenshot({ path: path.join(OUT, `msgs-rounds-${a}-${b}.png`), clip: box });
    log(`element screenshot: tests/artifacts/msgs-rounds-${a}-${b}.png${fits ? "" : " (group taller than the view: top part only)"}`);
  }

  // narrow screen: same page, same conversation
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(300);
  check("narrow: settings drawer collapsed", await page.$eval("#sidebar", (e) => e.hasAttribute("inert")));
  check("narrow: no horizontal overflow", !(await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth)));
  await page.$eval("#log", (l) => { l.scrollTop = l.scrollHeight; });
  await page.screenshot({ path: path.join(OUT, "05-narrow-390x844-latest.png") });
  await page.evaluate(() => document.querySelectorAll("#logInner .msg")[10].scrollIntoView({ block: "start" }));
  await page.screenshot({ path: path.join(OUT, "06-narrow-390x844-switch-to-astra.png") });
  await page.click("#menuBtn"); await page.waitForTimeout(300);
  check("narrow: drawer opens from the menu button", await page.$eval("#sidebar", (e) => !e.hasAttribute("inert")));
  await page.screenshot({ path: path.join(OUT, "07-narrow-390x844-drawer.png") });
  await page.keyboard.press("Escape");
  await page.setViewportSize({ width: 1440, height: 1000 });

  // download the conversation through the UI
  const [dl] = await Promise.all([page.waitForEvent("download"), page.click("#downloadBtn")]);
  const convPath = path.join(OUT, "conversation.json");
  await dl.saveAs(convPath);
  const conv = fs.readFileSync(convPath, "utf8");
  check("downloaded conversation has all 20 messages", JSON.parse(conv).messages.length === transcript.length * 2, dl.suggestedFilename());
  check("conversation JSON has no token", !conv.includes(TOKEN) && !/bearer/i.test(conv));

  const store = await page.evaluate(() => ({ ls: localStorage.length, ss: sessionStorage.length, cookie: document.cookie, url: location.href }));
  check("nothing stored in the browser; token not in URL", store.ls === 0 && store.ss === 0 && store.cookie === "" && !store.url.includes(TOKEN));
  const outside = [...new Set(requests.filter((u) => !u.startsWith(origin + "/") && !u.startsWith("data:") && !u.startsWith("blob:")))];
  check("no request left the app origin (no CDN, fonts, libraries)", outside.length === 0,
    `${requests.length} requests, ${[...new Set(requests.map((u) => new URL(u, origin).pathname))].join(" ")}${outside.length ? " OUTSIDE: " + outside.join(" ") : ""}`);

  fs.writeFileSync(path.join(OUT, "rounds.json"), JSON.stringify({ test_url: BASE + "/", rounds: transcript }, null, 2));
  await browser.close();
  log(`${results.filter(Boolean).length}/${results.length} checks passed; rounds completed: ${transcript.length}/10`);
  fs.writeFileSync(path.join(OUT, "e2e-run.log"), logLines.join("\n") + "\n");
  process.exit(results.every(Boolean) && transcript.length === 10 ? 0 : 1);
})().catch((e) => {
  log("ERROR " + (e && e.message ? e.message : e));
  fs.writeFileSync(path.join(OUT, "e2e-run.log"), logLines.join("\n") + "\n");
  process.exit(1);
});
