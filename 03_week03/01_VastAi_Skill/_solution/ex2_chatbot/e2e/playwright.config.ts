import { defineConfig, devices } from "@playwright/test";

// เปลี่ยนที่อยู่เว็บได้ด้วย BASE_URL เช่น  BASE_URL=http://localhost:3300 npx playwright test
const BASE_URL = process.env.BASE_URL || "http://localhost:3300";

export default defineConfig({
  testDir: "./tests",
  workers: 1, // รันทีละเคส (ให้วิดีโออ่านง่าย และไม่ยิง LLM พร้อมกัน)
  fullyParallel: false,
  retries: 0,
  timeout: 6 * 60 * 1000, // ต่อ 1 เคส (LLM จริงอาจตอบช้า)
  expect: { timeout: 90_000 }, // รอคำตอบแต่ละครั้งได้ถึง 90 วินาที
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: BASE_URL,
    viewport: { width: 1000, height: 720 },
    video: { mode: "on", size: { width: 1000, height: 720 } },
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
    locale: "th-TH",
    timezoneId: "Asia/Bangkok",
    actionTimeout: 30_000,
    launchOptions: { slowMo: 40 }, // หน่วงทุก action นิดหน่อย ให้คนดูตามทัน
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"], viewport: { width: 1000, height: 720 } } }],
});
