import { defineConfig, devices } from "@playwright/test";

// เปลี่ยนที่อยู่เว็บได้ด้วย BASE_URL เช่น  BASE_URL=http://localhost:3300 npx playwright test
const BASE_URL = process.env.BASE_URL || "http://localhost:3300";

export default defineConfig({
  testDir: "./tests",
  workers: Number(process.env.WORKERS || 2), // รันพร้อมกันน้อย ๆ ไม่ให้ LLM ตัวเดียวรับงานหนักเกิน
  fullyParallel: true, // ทุกเคสเป็นอิสระต่อกัน (แชทใหม่ทุกเคส) จึงรันพร้อมกันได้
  retries: 0,
  timeout: 15 * 60 * 1000, // ต่อ 1 เคส (เคสจองมีหลายข้อความ และ LLM จริงอาจตอบช้า)
  reporter: [["list"]],
  use: {
    baseURL: BASE_URL,
    viewport: { width: 1000, height: 720 },
    video: { mode: "on", size: { width: 1000, height: 720 } },
    locale: "th-TH",
    timezoneId: "Asia/Bangkok",
    actionTimeout: 30_000,
    // slowMo: หน่วงทุก action นิดหน่อยให้คนดูตามทัน · ปิด smooth scroll: หน้าจอเลื่อนทีเดียวจบ GIF จึงเล็กลงมาก
    launchOptions: { slowMo: 40, args: ["--disable-smooth-scrolling"] },
    contextOptions: { reducedMotion: "reduce" },
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"], viewport: { width: 1000, height: 720 } } }],
});
