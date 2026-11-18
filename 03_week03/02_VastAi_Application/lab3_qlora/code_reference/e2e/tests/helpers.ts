import { expect, test as base, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

export const OUT_DIR = path.join(__dirname, "..", "out");

// รอคำตอบ 1 ข้อความได้นานสุดเท่านี้ (LLM จริงอาจช้า) — ปรับได้ด้วย ANSWER_TIMEOUT_MS
export const ANSWER_TIMEOUT = Number(process.env.ANSWER_TIMEOUT_MS || 180_000);
const READ_PAUSE = 1200; // หยุดให้คนอ่านคำตอบระหว่างข้อความ (ms)
export const FINAL_HOLD = 4000; // ค้างหน้าจอหลังคำตอบสุดท้าย (ms)

// ---------- fixture: บันทึกหน้าจอของแต่ละเคส ----------
// ชื่อเคส = ข้อความก่อน ":" ในชื่อเทสต์ เช่น "case1-hours: ..."
// 1) วิดีโอของ Playwright        -> out/videos/<เคส>.webm
// 2) ภาพหน้าจอทุกครั้งที่จอเปลี่ยน   -> out/frames/<เคส>/ (ใช้ทำ GIF เพราะคมและไฟล์เล็กกว่าแปลงจากวิดีโอมาก)
export const test = base.extend<{ autoRecord: void }>({
  autoRecord: [
    async ({ page }, use, testInfo) => {
      const name = testInfo.title.split(":")[0].trim();
      const frameDir = path.join(OUT_DIR, "frames", name);
      fs.rmSync(frameDir, { recursive: true, force: true });
      fs.mkdirSync(frameDir, { recursive: true });

      // ขอภาพหน้าจอจาก Chromium โดยตรง (screencast) พร้อมเวลาของแต่ละภาพ
      const index: string[] = []; // บรรทัดละ "<เวลาเป็นวินาที> <ชื่อไฟล์>"
      const cdp = await page.context().newCDPSession(page);
      cdp.on("Page.screencastFrame", (f) => {
        const file = String(index.length).padStart(5, "0") + ".jpg";
        fs.writeFileSync(path.join(frameDir, file), Buffer.from(f.data, "base64"));
        index.push(`${f.metadata.timestamp} ${file}`);
        cdp.send("Page.screencastFrameAck", { sessionId: f.sessionId }).catch(() => {});
      });
      await cdp.send("Page.startScreencast", { format: "jpeg", quality: 92 });

      await use();

      await cdp.send("Page.stopScreencast").catch(() => {});
      index.push(`${Date.now() / 1000} END`); // เวลาจบ = ภาพสุดท้ายค้างถึงตรงนี้
      fs.writeFileSync(path.join(frameDir, "frames.txt"), index.join("\n") + "\n");

      const video = page.video();
      await page.close(); // ต้องปิดหน้าก่อน วิดีโอจึงจะเขียนครบ
      if (video) {
        const dir = path.join(OUT_DIR, "videos");
        fs.mkdirSync(dir, { recursive: true });
        await video.saveAs(path.join(dir, `${name}.webm`));
      }
    },
    { auto: true },
  ],
});
export { expect };

const bubbles = (page: Page, role: "user" | "assistant") =>
  page.locator(`[data-testid="message-bubble"][data-role="${role}"]`);

export async function openChat(page: Page) {
  await page.goto("/");
  await expect(page.getByTestId("chat-input")).toBeVisible();
  await expect(bubbles(page, "assistant").first()).toBeVisible(); // ข้อความต้อนรับ
  await page.waitForTimeout(600);
}

/**
 * รอจนบอทตอบเสร็จ แล้วคืนข้อความคำตอบ
 * หน้าแชทตั้ง data-busy="true" ตั้งแต่กดส่งจนคำตอบ stream จบ (รวมการ์ดจอง) -> รอจนกลับเป็น "false"
 */
async function waitForAnswer(page: Page, usersBefore: number, botsBefore: number): Promise<string> {
  await expect(bubbles(page, "user")).toHaveCount(usersBefore + 1); // ข้อความของเราขึ้นแล้ว = เริ่ม busy แล้ว
  await expect(page.getByTestId("message-list")).toHaveAttribute("data-busy", "false", { timeout: ANSWER_TIMEOUT });
  const bots = bubbles(page, "assistant");
  // ถ้าบอทตอบเป็นการ์ดจองอย่างเดียว จะไม่มีกล่องข้อความใหม่ -> คืนข้อความว่าง
  const text = (await bots.count()) > botsBefore ? (await bots.last().innerText()).trim() : "";
  await page.waitForTimeout(READ_PAUSE);
  return text;
}

/** พิมพ์ข้อความแบบเห็นการพิมพ์ทีละตัว แล้วกดส่ง -> คืนคำตอบของบอท */
export async function ask(page: Page, message: string): Promise<string> {
  const users = await bubbles(page, "user").count();
  const bots = await bubbles(page, "assistant").count();
  const input = page.getByTestId("chat-input");
  await input.click();
  await input.pressSequentially(message, { delay: 25 });
  await page.waitForTimeout(300);
  await page.getByTestId("send-button").click();
  return waitForAnswer(page, users, bots);
}

/** กดปุ่มลัด (price|hours|backpain|promo|book) -> คืนคำตอบของบอท */
export async function clickChip(page: Page, chip: string): Promise<string> {
  const users = await bubbles(page, "user").count();
  const bots = await bubbles(page, "assistant").count();
  const btn = page.locator(`[data-testid="quick-reply-chip"][data-chip="${chip}"]`);
  await btn.hover();
  await page.waitForTimeout(500);
  await btn.click();
  return waitForAnswer(page, users, bots);
}
