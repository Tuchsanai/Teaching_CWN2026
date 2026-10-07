# Image brief (สำหรับ cyolo / Codex imagegen)

สร้างภาพแนวคิด (concept infographic) สำหรับบทเรียน "ติดตั้ง Playwright บน Windows" ทั้งหมด 6 ภาพ
สไตล์: infographic พื้นขาว เส้นขอบโค้งมน สีฟ้า/แดง/เขียว/ส้ม ตัวหนังสือชัด ภาษาไทยปนอังกฤษ ไอคอน Playwright เป็นหน้ากากละครเขียว-แดง
ขนาดแนวนอน 1536x1024 ห้ามมีตัวสะกดผิดในคำสั่ง (คำสั่งให้ใช้ฟอนต์ monospace)

1. concept-01-stack.png — "ชั้นของเครื่องมือ" ซ้อนจากล่างขึ้นบน: Windows 11 → Node.js + npm → @playwright/test (test runner) และ @playwright/mcp (MCP server) → เบราว์เซอร์ (Chromium / Firefox / WebKit ของ Playwright ที่ %LocalAppData%\ms-playwright และ Chrome / Edge ที่ติดตั้งในเครื่อง) → ด้านบนสุด: "คุณเขียน test" และ "Claude Code สั่งผ่าน MCP"
2. concept-02-test-vs-mcp.png — เปรียบเทียบ 2 กล่อง: ซ้าย "Playwright Test" (ไฟล์ .spec.ts → npx playwright test → ผ่าน/ไม่ผ่าน + HTML report) ขวา "Playwright MCP" (Claude Code → tools/call browser_navigate → เบราว์เซอร์ → screenshot) กล่องล่าง "engine เดียวกัน: Playwright"
3. concept-03-update-flow.png — flow 5 ขั้น เป็นลูกศรเรียงกัน: 1 ตรวจเวอร์ชัน → 2 ตารางสรุป + ถามยืนยัน (ไอคอนมือยกหยุด) → 3 อัปเดตเฉพาะที่เก่า → 4 ตรวจ MCP config / extension → 5 ทดสอบ example.com + ตาราง ก่อน/หลัง
4. concept-04-npx-cache.png — อธิบาย npx cache: คำสั่ง "npx -y @playwright/mcp@latest" → ถ้ามีใน %LocalAppData%\npm-cache\_npx แล้ว อาจใช้ของเก่า → ล้างโฟลเดอร์ _npx → npx ดึงเวอร์ชันล่าสุดจาก npm registry ใหม่
5. concept-05-test-anatomy.png — กายวิภาคไฟล์ test: แสดงโค้ด
   import { test, expect } from '@playwright/test';
   test('has title', async ({ page }) => {
     await page.goto('https://example.com');
     await expect(page).toHaveTitle(/Example Domain/);
   });
   พร้อมป้ายลูกศรชี้: test() = 1 กรณีทดสอบ, page = แท็บเบราว์เซอร์ใหม่ที่สะอาด, goto = เปิดเว็บ, expect = ตรวจผล (รอให้อัตโนมัติ)
6. concept-06-extension-mode.png — โหมดของ Playwright MCP 2 แบบ: ซ้าย "ค่าเริ่มต้น" เปิดเบราว์เซอร์แยกใหม่ (profile สะอาด ไม่มีล็อกอิน) ขวา "--extension" ต่อเข้า Chrome จริงของคุณผ่านส่วนขยาย "Playwright MCP Bridge" (เห็นแท็บที่ล็อกอินไว้) มีป้ายเตือนสีส้ม "AI เห็นบัญชีที่ล็อกอินอยู่ ใช้อย่างระวัง"

บันทึกไฟล์สุดท้ายลงโฟลเดอร์ img/ ของบทเรียนนี้ด้วยชื่อไฟล์ตามที่กำหนด
