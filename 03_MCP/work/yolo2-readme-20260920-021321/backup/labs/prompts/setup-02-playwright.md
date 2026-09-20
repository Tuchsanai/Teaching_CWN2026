# Setup Prompt S2 — ติดตั้งเฉพาะ Playwright MCP

```text
ติดตั้งและลงทะเบียน Playwright MCP ให้ Claude Code บนเครื่องนี้ โดยไม่ต้องถามกลับ
1. ตรวจว่ามี node และ npm (รายงานเวอร์ชัน)
2. npm install -g @playwright/mcp แล้ว npx playwright install chromium (บน Linux ให้ npx playwright install-deps chromium ด้วย ถ้าต้องใช้ sudo และรันไม่ได้ ให้บอกคำสั่งที่ผู้ใช้ต้องรันเอง)
3. ตรวจว่าเครื่องนี้มีจอแสดงผลหรือไม่ (เช่น ตัวแปร DISPLAY บน Linux, หรือเป็น macOS/Windows) ถ้าไม่มีจอให้ลงทะเบียนแบบ headless
4. claude mcp add --scope user playwright -- <path เต็มของ playwright-mcp> --browser chromium [--headless ถ้าไม่มีจอ] [--no-sandbox ถ้ารันเป็น root] (ถ้ามีชื่อ playwright อยู่แล้วให้ remove ก่อน) — ต้องใส่ --browser chromium เพราะ @playwright/mcp รุ่นใหม่ใช้ Google Chrome เป็นค่าเริ่มต้น
5. claude mcp list แล้วรายงานสถานะ ถ้าไม่ Connected ให้แก้จนผ่าน แล้วบอกผู้ใช้ให้พิมพ์ /exit และเปิด claude ใหม่
```

**ตรวจอย่างไรว่าพรอมป์ต์นี้ทำงานสำเร็จ**

**วิธีอ่านผล:** ตัวอย่างด้านล่างเป็น **ผลที่คาดหวัง (Expected output)** เพื่อใช้ตรวจงาน ไม่ใช่ผลรันใหม่หรือข้อความที่ Host ต้องตอบตรงทุกตัวอักษร ค่า path ชื่อไฟล์ และเวลาจะแตกต่างกันได้ ต้องมีผลจาก tool หรือไฟล์จริงรองรับคำว่า “ผ่าน”

**ทดสอบหลังติดตั้ง:** เปิด Host เป็น session ใหม่ ใช้หน้าเว็บสาธารณะเพื่อทดสอบเบราว์เซอร์ก่อน โดยยังไม่ต้องติดตั้ง Kokoro

```text
ใช้ Playwright MCP เปิด https://example.com ทำ accessibility snapshot แล้วรายงานชื่อหน้า หัวข้อหลัก และถ่าย screenshot พร้อม path ของไฟล์
```

**ตัวอย่างผลที่ควรเห็น**

```text
browser_navigate → เปิดหน้าได้
ชื่อหน้า / หัวข้อหลัก: Example Domain
browser_snapshot → มี heading และ link ของหน้าเว็บ
browser_take_screenshot → ได้ไฟล์ภาพหน้าเว็บ
```

**ผ่านเมื่อ:** เปิดเว็บ อ่าน snapshot และได้ screenshot จริง หากเครือข่ายเข้าเว็บนี้ไม่ได้ ให้ใช้หน้าเว็บที่เข้าถึงได้แทนและระบุ URL ที่ทดสอบ เมื่อทำ S3 แล้วจึงใช้ S5 ทดสอบกรอกฟอร์มและคลิก Speak เพิ่มเติม


