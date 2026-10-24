// ใช้: node rea\record-har.mjs [--out out\after]  (รันจากรากบท · ต้องมี npm install ใน rea\)
// record-har.mjs — เดินเส้นทางหลักของ PawPantry แบบ headless แล้วบันทึก HAR ให้ REA อ่าน
// ตัวเลือก: --base <url> (หรือ env BASE_URL · ค่าเริ่มต้น http://127.0.0.1:4000 · localhost ถูกแปลงเป็น 127.0.0.1)
//           --out <โฟลเดอร์> (หรือ env OUT_DIR · relative = จากโฟลเดอร์ที่รัน · ค่าเริ่มต้น <รากบท>/out)
// ผลลัพธ์: <out>/pawpantry-main.har + <out>/har-steps.json (สรุปแต่ละขั้น)
// เส้นทาง: reset → home → search → product → add to cart → coupon PAW10 → login demo → checkout → place order
import { chromium } from "playwright";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const args = process.argv.slice(2);
const opt = (name) => {
  const i = args.indexOf(name);
  if (i === -1) return undefined;
  const v = args[i + 1];
  if (!v || v.startsWith("--")) {
    console.error(`usage: node rea/record-har.mjs [--base <url>] [--out <dir>]  (${name} ต้องมีค่า)`);
    process.exit(2);
  }
  return v;
};
// ใช้ 127.0.0.1 ไม่ใช่ localhost: บน Windows localhost ไปทาง IPv6 แล้ว HAR ได้ serverIPAddress "[::1]"
// ซึ่ง REA inspect-web-network-capture ไม่รับ (HAR schema validation failed: format)
const baseUrl = new URL(opt("--base") ?? process.env.BASE_URL ?? "http://127.0.0.1:4000");
if (baseUrl.hostname === "localhost") {
  baseUrl.hostname = "127.0.0.1";
  console.log(`(ใช้ ${baseUrl.origin} แทน localhost เพื่อให้ REA อ่าน HAR ได้)`);
}
const BASE = baseUrl.href.replace(/\/+$/, "");
const outArg = opt("--out") ?? process.env.OUT_DIR;
const OUT = outArg ? resolve(process.cwd(), outArg) : resolve(dirname(fileURLToPath(import.meta.url)), "..", "out");
mkdirSync(OUT, { recursive: true });
const harPath = join(OUT, "pawpantry-main.har");
const steps = [];
const t0 = Date.now();

let browser;
let page;
const step = async (name, fn) => {
  const s = Date.now();
  try {
    await fn();
  } catch (e) {
    console.error(`✗ ${name}: ${e?.message ?? e}`);
    await browser?.close().catch(() => {});
    process.exit(1);
  }
  steps.push({ step: name, ms: Date.now() - s, url: page.url() });
  console.log(`✓ ${name}  (${Date.now() - s} ms)  ${page.url()}`);
};

// รีเซ็ตข้อมูลฝั่ง server ก่อน (ต้องเปิด ALLOW_TEST_RESET=1)
await fetch(`${BASE}/api/test/reset`, { method: "POST" }).catch(() => {});

browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  baseURL: BASE,
  // content: "embed" → body อยู่ใน HAR (REA อ่าน request/response body ได้) · urlFilter ตัด font/รูป/_next/image ออกให้ไฟล์เล็ก
  recordHar: { path: harPath, content: "embed", mode: "full", urlFilter: /^(?!.*(\.(woff2?|png|jpe?g|svg|ico|webp)(\?|$)|\/_next\/image)).*$/ },
});
page = await context.newPage();

await step("01 home", async () => {
  await page.goto("/");
  await page.getByTestId("hero").waitFor();
});
await step("02 search 'แซลมอน'", async () => {
  await page.getByTestId("search-input").fill("แซลมอน");
  await page.getByTestId("search-submit").click();
  await page.waitForURL(/\/products\?q=/);
  await page.getByTestId("product-card").first().waitFor();
});
await step("03 open product", async () => {
  await page.getByTestId("product-name").first().click();
  await page.getByTestId("add-to-cart").waitFor();
});
await step("04 add to cart (x3)", async () => {
  await page.getByTestId("qty-plus").click();
  await page.getByTestId("qty-plus").click();
  await page.getByTestId("add-to-cart").click();
  await page.waitForTimeout(300);
});
await step("05 cart + coupon PAW10", async () => {
  await page.goto("/cart");
  await page.getByTestId("coupon-input").fill("PAW10");
  const resp = page.waitForResponse((r) => r.url().includes("/api/coupons/validate"));
  await page.getByTestId("coupon-apply").click();
  await resp;
  await page.getByTestId("coupon-message").waitFor();
});
await step("06 checkout → redirect login", async () => {
  await page.getByTestId("checkout-button").click();
  await page.waitForURL(/\/login/);
});
await step("07 login demo@pawpantry.test", async () => {
  await page.getByTestId("login-email").fill("demo@pawpantry.test");
  await page.getByTestId("login-password").fill("Paw12345");
  await page.getByTestId("login-submit").click();
  await page.waitForURL((u) => u.pathname === "/checkout"); // อย่าใช้ /\/checkout/ เพราะจะ match "/login?next=/checkout"
});
await step("08 fill shipping + place order", async () => {
  await page.getByTestId("ship-name").fill("สมชาย ทดสอบ");
  await page.getByTestId("ship-phone").fill("0812345678");
  await page.getByTestId("ship-postcode").fill("10110");
  await page.getByTestId("ship-address").fill("99 ถนนสุขุมวิท แขวงคลองเตย");
  await page.getByTestId("pay-cod").check().catch(() => page.getByTestId("pay-cod").click());
  await page.getByTestId("place-order").click();
  await page.getByTestId("order-success").waitFor({ timeout: 15000 });
});

await context.close(); // HAR ถูกเขียนตอนปิด context
await browser.close();
writeFileSync(join(OUT, "har-steps.json"), JSON.stringify({ base: BASE, out: OUT, total_ms: Date.now() - t0, steps }, null, 2));
console.log(`HAR → ${harPath}`);
