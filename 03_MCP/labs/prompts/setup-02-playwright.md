# Setup Prompt S2 — ติดตั้งเฉพาะ Playwright MCP

```text
ติดตั้งและลงทะเบียน Playwright MCP ให้ Claude Code บนเครื่องนี้ โดยไม่ต้องถามกลับ
1. ตรวจว่ามี node และ npm (รายงานเวอร์ชัน)
2. npm install -g @playwright/mcp แล้ว npx playwright install chromium (บน Linux ให้ npx playwright install-deps chromium ด้วย ถ้าต้องใช้ sudo และรันไม่ได้ ให้บอกคำสั่งที่ผู้ใช้ต้องรันเอง)
3. ตรวจว่าเครื่องนี้มีจอแสดงผลหรือไม่ (เช่น ตัวแปร DISPLAY บน Linux, หรือเป็น macOS/Windows) ถ้าไม่มีจอให้ลงทะเบียนแบบ headless
4. claude mcp add --scope user playwright -- <path เต็มของ playwright-mcp> --browser chromium [--headless ถ้าไม่มีจอ] [--no-sandbox ถ้ารันเป็น root] (ถ้ามีชื่อ playwright อยู่แล้วให้ remove ก่อน) — ต้องใส่ --browser chromium เพราะ @playwright/mcp รุ่นใหม่ใช้ Google Chrome เป็นค่าเริ่มต้น
5. claude mcp list แล้วรายงานสถานะ ถ้าไม่ Connected ให้แก้จนผ่าน แล้วบอกผู้ใช้ให้พิมพ์ /exit และเปิด claude ใหม่
```
