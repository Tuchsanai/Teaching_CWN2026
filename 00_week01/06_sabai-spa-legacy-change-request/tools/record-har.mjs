// record-har.mjs — บันทึก HAR ของเส้นทางหลักสบายใจ สปา ด้วย Playwright แบบ headless
// ใช้: node record-har.mjs [BASE_URL] [OUT.har]   (ค่าเริ่ม http://127.0.0.1:4000 , sabai-journeys.har)
// ใช้ 127.0.0.1 ไม่ใช่ localhost: ถ้าเป็น localhost Playwright เขียน serverIPAddress "[::1]" แล้ว REA ไม่รับ HAR (HAR schema validation failed)
// เส้นทาง: services → จองแบบไม่ล็อกอิน (เลือกรอบ → ใบสรุปราคา → ยืนยัน) → ล็อกอินคุณนิดา → นัดของฉัน → ยกเลิก B05 → ล็อกอินเจ้าของร้าน → /admin
import { chromium } from "@playwright/test";

const BASE = process.argv[2] ?? "http://127.0.0.1:4000";
const OUT = process.argv[3] ?? "sabai-journeys.har";
const DATE = "2026-10-12"; // TODAY ในโหมดทดสอบ = 2026-10-10 10:00 → จองได้ตั้งแต่พรุ่งนี้
const t0 = Date.now();
const log = (m) => console.log(`[${((Date.now() - t0) / 1000).toFixed(1)}s] ${m}`);

const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext({ baseURL: BASE, recordHar: { path: OUT, content: "embed", mode: "full" } });
const page = await ctx.newPage();

// 0) รีเซ็ตข้อมูลทดสอบให้เริ่มจาก seed เดิมทุกครั้ง
const rs = await ctx.request.post("/api/test/reset");
log(`reset ${rs.status()} ${await rs.text()}`);

// 1) ดูรายการบริการ
await page.goto("/services");
await page.getByTestId("service-card-S01").waitFor();
log("services ok");

// 2) จองแบบไม่ล็อกอิน: S01 เดี่ยว 1 คน
await page.getByTestId("service-book-S01").click();
await page.getByTestId("book-next-1").click();
await page.getByTestId("book-date").fill(DATE);
await page.getByTestId("book-slots").waitFor();
await page.getByTestId("book-slot-15:00").click();
await page.getByTestId("book-next-2").click();
await page.getByTestId("book-contact-name").fill("คุณทดสอบ HAR");
await page.getByTestId("book-contact-phone").fill("081-555-0101");
await page.getByTestId("book-quote-total").filter({ hasText: "฿" }).waitFor();
log(`quote total = ${(await page.getByTestId("book-quote-total").innerText()).trim()}`);
await page.getByTestId("book-next-3").click();
await page.getByTestId("book-summary").waitFor();
await page.getByTestId("book-confirm").click();
await page.getByTestId("booking-done").waitFor();
log(`booked ${(await page.getByTestId("booking-code").textContent()).trim()}`);

// 3) ล็อกอินสมาชิก U01 คุณนิดา (TEST-DATA) → นัดของฉัน
async function login(email, password, next) {
  await page.goto(`/login?next=${next}`);
  await page.getByTestId("login-email").fill(email);
  await page.getByTestId("login-password").fill(password);
  await page.getByTestId("login-submit").click();
  await page.waitForURL((u) => !u.pathname.startsWith("/login"));
}
await login("nida@sabai.test", "Nida@2026", "/account");
await page.getByTestId("history-list").waitFor();
log(`account: ${await page.getByTestId("history-list").locator("li").count()} bookings`);

// 4) ยกเลิก B05 (เหลือ 24 ชม. พอดี → ยกเลิกได้ BR-07) · B06 ต้องกดไม่ได้
log(`B06 cancel disabled = ${await page.getByTestId("cancel-B06").isDisabled()}`);
await page.getByTestId("cancel-B05").click();
await page.getByTestId("cancel-confirm-B05").click();
await page.getByTestId("cancel-result-B05").waitFor();
log(`cancel B05: ${(await page.getByTestId("cancel-result-B05").innerText()).trim()}`);

// 5) ออกจากระบบ → เจ้าของร้าน → /admin
await page.getByTestId("logout-button").click();
await page.getByTestId("nav-login").waitFor();
await login("owner@sabai.test", "Owner@2026", "/admin");
await page.getByTestId("admin-date").waitFor();
await page.getByTestId("admin-date").fill(DATE);
await page.getByTestId("admin-table").waitFor();
log(`admin rows on ${DATE}: ${await page.getByTestId("admin-table").locator("tbody tr").count()}`);

await ctx.close(); // เขียนไฟล์ HAR ตอนปิด context
await browser.close();
log(`HAR saved → ${OUT}`);
