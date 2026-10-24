import { ask, clickChip, expect, openChat, test } from "./helpers";

// ข้อความตรวจคำตอบแบบ "หลวม ๆ" เพราะ LLM จริงตอบไม่เหมือนเดิมทุกครั้ง

test("case1-hours: ทักทาย + ถามเวลาเปิดปิด", async ({ page }) => {
  await openChat(page);
  const hi = await ask(page, "สวัสดีค่ะ");
  expect(hi).toMatch(/สวัสดี|ยินดี|ค่ะ|คะ/);

  const hours = await ask(page, "ร้านเปิดกี่โมงถึงกี่โมงคะ");
  expect(hours).toMatch(/10/);
  expect(hours).toMatch(/22/);
});

test("case2-price: ถามราคาด้วยปุ่ม ดูราคา", async ({ page }) => {
  await openChat(page);
  const price = await clickChip(page, "price");
  expect(price).toMatch(/บาท|฿/);
  expect(price).toMatch(/\d{3}/); // มีตัวเลขราคา เช่น 350
  expect(price).toMatch(/นวด/);
});

test("case3-backpain: ขอคำแนะนำนวดแก้ปวดหลัง ออฟฟิศซินโดรม", async ({ page }) => {
  await openChat(page);
  const tip = await ask(page, "ทำงานออฟฟิศนั่งหน้าคอมทั้งวัน ปวดหลังกับบ่ามากเลยค่ะ แนะนำนวดแบบไหนดีคะ");
  expect(tip).toMatch(/นวด/);
  expect(tip).toMatch(/หลัง|บ่า|ไหล่|ประคบ/);
});

test("case4-promo: ถามโปรโมชั่น", async ({ page }) => {
  await openChat(page);
  const promo = await ask(page, "ตอนนี้มีโปรโมชั่นอะไรบ้างคะ");
  expect(promo).toMatch(/ลด|%|แถม|ฟรี/);

  const student = await ask(page, "เป็นนักศึกษา ได้ส่วนลดไหมคะ");
  expect(student).toMatch(/นักศึกษา|15|ลด/);
});

test("case5-booking: จองคิวหลายขั้น แล้วเห็นในหน้ารายการจอง", async ({ page }) => {
  await openChat(page);
  const card = page.getByTestId("booking-card");

  // เริ่มด้วยปุ่ม "จองคิว" แล้วค่อย ๆ ให้ข้อมูลทีละอย่าง (บอทควรถามสิ่งที่ยังขาด)
  const first = await clickChip(page, "book");
  expect(first).toMatch(/ชื่อ|เบอร์|บริการ|วัน|เวลา|จอง/);

  const steps = [
    "ชื่อ มานี ใจดี ค่ะ",
    "เบอร์ 089-555-1234 ค่ะ",
    "ขอนวดไทยแผนโบราณ 60 นาทีค่ะ",
    "วันที่ 2026-10-25 เวลา 15:00 ค่ะ",
    // ถ้า LLM จริงขอให้ยืนยันก่อน จะส่งข้อความนี้ (mock จะจองเสร็จก่อนถึงตรงนี้)
    "ข้อมูลถูกต้องค่ะ ยืนยันเลยค่ะ",
    "ถูกต้องทั้งหมดค่ะ ยืนยันได้เลยค่ะ",
  ];
  for (const msg of steps) {
    if (await card.isVisible()) break;
    await ask(page, msg);
  }

  await expect(card).toBeVisible();
  await expect(page.getByTestId("booking-error")).toHaveCount(0);
  await expect(page.getByTestId("booking-card-name")).toContainText("มานี");
  expect((await page.getByTestId("booking-card-phone").innerText()).replace(/\D/g, "")).toContain("0895551234");
  await expect(page.getByTestId("booking-card-service")).toContainText("นวดไทย");
  await expect(page.getByTestId("booking-card-time")).toContainText("2026-10-25 15:00");
  const bookingId = await card.getAttribute("data-booking-id");
  await card.scrollIntoViewIfNeeded();
  await page.waitForTimeout(2000);

  // ไปหน้า /bookings -> ต้องเห็นแถวใหม่ที่ดึงมาจาก PostgreSQL
  await page.getByTestId("nav-bookings").click();
  await expect(page).toHaveURL(/\/bookings/);
  await expect(page.getByTestId("bookings-table")).toBeVisible();
  const row = page.locator(`[data-testid="booking-row"][data-booking-id="${bookingId}"]`);
  await expect(row).toBeVisible();
  await expect(row.getByTestId("booking-row-name")).toContainText("มานี");
  await expect(row.getByTestId("booking-row-service")).toContainText("นวดไทย");
  await expect(row.getByTestId("booking-row-time")).toHaveText("2026-10-25 15:00");
  await row.hover();
  await page.waitForTimeout(2500);
});

test("case6-offtopic: ถามนอกเรื่อง บอทตอบสุภาพและวกกลับเรื่องร้าน", async ({ page }) => {
  await openChat(page);
  const reply = await ask(page, "ขอสูตรทำต้มยำกุ้งหน่อยได้ไหมคะ");
  expect(reply).toMatch(/ค่ะ|คะ|ขออภัย|ขอโทษ/); // สุภาพ
  expect(reply).toMatch(/นวด|ร้าน|บริการ|ราคา|จอง/); // พากลับมาเรื่องร้าน
  expect(reply).not.toMatch(/น้ำพริกเผา|ข่า.*ตะไคร้.*มะนาว/); // ไม่ควรให้สูตรอาหาร
});

test("case7-english: ลูกค้าพิมพ์ภาษาอังกฤษ", async ({ page }) => {
  await openChat(page);
  const reply = await ask(page, "Hello! How much is a 1 hour Thai massage?");
  expect(reply.length).toBeGreaterThan(5);
  expect(reply).toMatch(/\d|ค่ะ|massage|นวด|สวัสดี/i);
});
