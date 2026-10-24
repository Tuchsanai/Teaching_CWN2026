// record-har.mjs — เดินเส้นทางหลักของ PawPantry แบบ headless แล้วบันทึก HAR ให้ REA อ่าน
// ใช้:  BASE_URL=http://localhost:3000 node record-har.mjs   (ต้องมีแพ็กเกจ playwright 1.63)
// ผลลัพธ์: out/pawpantry-main.har + out/har-steps.json (สรุปแต่ละขั้น)
// เส้นทาง: home → search → product → add to cart → coupon PAW10 → login demo → checkout → place order
import { chromium } from "playwright";
import { mkdirSync, writeFileSync } from "node:fs";

const BASE = process.env.BASE_URL ?? "http://localhost:3000";
const OUT = process.env.OUT_DIR ?? "out";
mkdirSync(OUT, { recursive: true });
const harPath = `${OUT}/pawpantry-main.har`;
const steps = [];
const t0 = Date.now();
const step = async (name, fn) => {
  const s = Date.now();
  await fn();
  steps.push({ step: name, ms: Date.now() - s, url: page.url() });
  console.log(`✓ ${name}  (${Date.now() - s} ms)  ${page.url()}`);
};

// รีเซ็ตข้อมูลฝั่ง server ก่อน (ต้องเปิด ALLOW_TEST_RESET=1)
await fetch(`${BASE}/api/test/reset`, { method: "POST" }).catch(() => {});

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  baseURL: BASE,
  // content: "embed" → body อยู่ใน HAR (REA อ่าน request/response body ได้) · urlFilter ตัด font/รูป/_next/image ออกให้ไฟล์เล็ก
  recordHar: { path: harPath, content: "embed", mode: "full", urlFilter: /^(?!.*(\.(woff2?|png|jpe?g|svg|ico|webp)(\?|$)|\/_next\/image)).*$/ },
});
const page = await context.newPage();

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
await step("04 add to cart (x3 ให้ยอดถึงเงื่อนไขคูปอง)", async () => {
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
writeFileSync(`${OUT}/har-steps.json`, JSON.stringify({ base: BASE, total_ms: Date.now() - t0, steps }, null, 2));
console.log(`HAR → ${harPath}`);
