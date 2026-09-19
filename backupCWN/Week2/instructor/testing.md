# การทดสอบสำหรับผู้สอน/ผู้ดูแลแพ็กเกจ

ไม่เป็นกิจกรรมเขียนโค้ดของผู้เรียน หน้าเรียนและข้อมูลที่ส่งออกพร้อมใช้ ไม่ต้อง build เพื่อเปิดสไลด์

## เครื่องมือที่ใช้รอบนี้

- cyolo1 เรียก Codex CLI 0.154.0; login status: Logged in using ChatGPT
- Playwright CLI 1.58.2 ผ่าน `npx playwright test` (`playwright-cli` ไม่ได้ติดตั้ง จึงใช้ Test CLI ตามทางเลือกที่กำหนด)
- Chrome for Testing 153.0.8010.12 ที่ `/opt/ms-playwright/chromium-1243/chrome-linux64/chrome` เป็น executable ที่ติดตั้งอยู่ รุ่นนี้ไม่ใช่ browser bundle เริ่มต้นของ Playwright 1.58.2 แต่ผ่านชุดทดสอบที่ระบุ
- Excalidraw CLI mcp-excalidraw-server 2.0.0; owned canvas localhost:3017
- หน้าเรียน localhost:18761; ร้านฝึก localhost:18762; desktop 1440×1000, mobile 390×844; Lab guide mobile 390×900

เก็บ --help/--version และเวลาเช็คที่ [tool-help](../evidence/build/tool-help)

## ทำซ้ำเฉพาะการตรวจเว็บ (ไม่เสียโทเคน AI)

ผู้สอนติดตั้ง dependency ในพื้นที่ชั่วคราว หรือใช้ของห้องที่ตรงเวอร์ชัน ไม่ใส่ node_modules ในแพ็กเกจ:

```bash
npm install --prefix /tmp/week2-browser-tools @playwright/test@1.58.2
```

บนเครื่องที่ไม่มี browser พร้อม ให้ติดตั้ง Chromium ของ Playwright เป็นงาน setup ก่อนเรียน หน้า config จะใช้ executable ที่มีในเครื่องอ้างอิง ถ้าไม่มีจะใช้ bundle ที่ติดตั้งกับ Playwright ผู้สอนระบุ `WEEK2_CHROMIUM` ได้เมื่อจำเป็น ไม่ให้ผู้เรียนตั้งค่านี้

จาก Week2 เปิด server ใน Terminal ผู้สอน:

```bash
python3 -m http.server 18761 --bind 127.0.0.1
```

คำสั่งจริงในเครื่องอ้างอิง (Terminal อีกอัน):

```bash
cd /tmp/week2-browser-tools
NODE_PATH=/tmp/week2-browser-tools/node_modules npx playwright test -c /root/workspace/CWN/Teaching/Week2/instructor/runtime/playwright.config.cjs
```

หากย้ายแพ็กเกจ ผู้สอนใช้ path เต็มของ config ณ ตำแหน่งใหม่ ไม่แก้เนื้อหา test การรันจะ reset ร้านฝึกเฉพาะ checkout นี้ อย่าใช้ร้านฝึกเดียวกับกลุ่มที่กำลังทำงาน ผลดิบและ screenshots อยู่ evidence/browser

หลังจบปิด HTTP server ด้วย Ctrl+C ในหน้าต่างที่สร้าง และใช้ `./shop stop` ทดสอบไม่หยุดบริการอื่น

## การทดลองโมเดลและหลักฐาน

อ่าน protocol ก่อนรัน scripts experiments.py/confirmed_trials.py/transfer_and_creation.py เป็นบันทึกการทดลองที่รันแล้ว ไม่ใช่คำสั่งให้รันซ้ำทันที scripts ปฏิเสธ overwrite label เดิม ต้องกำหนด study ใหม่/พื้นที่ผลใหม่ก่อนทำซ้ำ การเรียกแต่ละครั้งใช้โควตา cyolo1 และไม่ retry อัตโนมัติ

JSONL คือข้อความและ tool events ที่ CLI แสดง -o คือไฟล์คำตอบจริง metadata เก็บ argv, UTC, monotonic seconds, usage และ errors snapshots เป็นข้อมูลเข้าเท่านั้น ไม่มีเฉลย การตรวจ native ใช้คำสั่งอ่านไฟล์ที่มี exit code 0 ไม่ใช้คำพูด AI เพียงอย่างเดียว

## ตรวจแพ็กเกจแบบ read-only

```bash
python3 instructor/runtime/audit_package.py
```

ตรวจลิงก์ภายใน ความเท่ากันของ body Prompt/Skill hashes ของ input snapshot และ fingerprint Week1 ถ้าย้ายแพ็กเกจโดยไม่มี Week1 รายการตรวจอนุรักษ์ Week1 จะไม่สามารถยืนยันซ้ำได้ ใช้ผลต้นทางที่บันทึกไว้แยกจากการตรวจไฟล์ใหม่
