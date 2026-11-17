import { expect, test as base, type Locator, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

// ---------- fixture: บันทึกวิดีโอของแต่ละเคสเป็น videos/<slug>.webm ----------
// slug = ข้อความก่อน ":" ในชื่อเทสต์ เช่น "case1-hours: ..." -> videos/case1-hours.webm
export const test = base.extend<{ autoVideo: void }>({
  autoVideo: [
    async ({ page }, use, testInfo) => {
      await use();
      const video = page.video();
      await page.waitForTimeout(1500); // ค้างหน้าจอสุดท้ายไว้นิดนึงในวิดีโอ
      await page.close();
      if (video) {
        const slug = testInfo.title.split(":")[0].trim();
        const dir = path.join(__dirname, "..", "videos");
        fs.mkdirSync(dir, { recursive: true });
        await video.saveAs(path.join(dir, `${slug}.webm`));
      }
    },
    { auto: true },
  ],
});
export { expect };

export const ANSWER_TIMEOUT = 90_000;

export async function openChat(page: Page) {
  await page.goto("/");
  await expect(page.getByTestId("chat-input")).toBeVisible();
  await expect(page.getByTestId("message-bubble").first()).toBeVisible(); // ข้อความต้อนรับ
  await page.waitForTimeout(800);
}

function assistantBubbles(page: Page): Locator {
  return page.locator('[data-testid="message-bubble"][data-role="assistant"]');
}

/** รอจนบอทตอบเสร็จ แล้วคืนข้อความคำตอบล่าสุด */
async function waitForAnswer(page: Page, before: number): Promise<string> {
  const bubbles = assistantBubbles(page);
  await expect(bubbles).toHaveCount(before + 1, { timeout: ANSWER_TIMEOUT });
  // ระหว่างที่บอทกำลังตอบ ปุ่ม quick-reply จะถูก disable -> รอจนกดได้อีกครั้ง = ตอบเสร็จ
  await expect(page.getByTestId("quick-reply-chip").first()).toBeEnabled({ timeout: ANSWER_TIMEOUT });
  await expect(page.getByTestId("typing-indicator")).toHaveCount(0);
  const text = (await bubbles.last().innerText()).trim();
  expect(text.length, "คำตอบของบอทต้องไม่ว่าง").toBeGreaterThan(0);
  await page.waitForTimeout(1800); // หยุดให้คนอ่านคำตอบในวิดีโอ
  return text;
}

/** พิมพ์ข้อความแบบเห็นการพิมพ์ทีละตัว แล้วกดส่ง -> คืนคำตอบของบอท */
export async function ask(page: Page, message: string): Promise<string> {
  const before = await assistantBubbles(page).count();
  const input = page.getByTestId("chat-input");
  await input.click();
  await input.pressSequentially(message, { delay: 45 });
  await page.waitForTimeout(400);
  await page.getByTestId("send-button").click();
  await expect(page.locator('[data-testid="message-bubble"][data-role="user"]').last()).toHaveText(message);
  return waitForAnswer(page, before);
}

/** กดปุ่ม quick-reply (price|hours|backpain|promo|book) -> คืนคำตอบของบอท */
export async function clickChip(page: Page, chip: string): Promise<string> {
  const before = await assistantBubbles(page).count();
  const btn = page.locator(`[data-testid="quick-reply-chip"][data-chip="${chip}"]`);
  await btn.hover();
  await page.waitForTimeout(500);
  await btn.click();
  return waitForAnswer(page, before);
}
