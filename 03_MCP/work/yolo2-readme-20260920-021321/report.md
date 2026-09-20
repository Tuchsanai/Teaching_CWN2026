# รายงานการแก้เอกสาร 03_MCP (yolo2 / Claude Code) — 20 กันยายน 2026

## ขอบเขตที่ทำจริง
แก้เอกสารเท่านั้น: `readme.md` และ `labs/prompts/setup-*.md` (8 ไฟล์)
ไม่ได้รันติดตั้ง ไม่ได้แก้ config ของ Host ไม่ได้เรียก MCP ไม่ได้แตะโค้ด server/รูป/ผลทดลองเดิม/credentials ไม่ได้ commit หรือ push
สำรองต้นฉบับก่อนแก้ไว้ที่ `backup/readme.md` และ `backup/labs/prompts/`

## การตรวจเอกสารต้นทาง (read-only)
- npm `mcp-excalidraw-server` (registry): latest 2.0.0, `repository.url` = `git+https://github.com/yctimlin/mcp_excalidraw.git`, bin = `mcp-excalidraw-server` / `excalidraw-canvas`
- README `yctimlin/mcp_excalidraw`: มี 3 ทาง (agent skill + CLI, MCP server stdio 26 tools, REST), Node ≥ 20, canvas เริ่มต้น `http://127.0.0.1:3000`, screenshot ต้องมีแท็บเบราว์เซอร์เปิด canvas
- README `microsoft/playwright-mcp`: Node ≥ 18, มีหัวข้อ Claude Code และ Codex โดยตรง, ตัวเลือก `--browser` / `--headless` / `--no-sandbox` (ตารางตัวเลือกระบุ chrome/firefox/webkit/msedge ส่วนตัวอย่าง Docker ของ repo ใช้ `--browser chromium`)
- README `hexgrad/kokoro`: เป็น inference library ของ Kokoro-82M (`pip install kokoro`, `KPipeline`, soundfile, 24000 Hz, espeak-ng) — ไม่มีคำว่า MCP และไม่มี MCP server มาให้

## สิ่งที่เปลี่ยนใน readme.md
1. 4.1 เขียนใหม่: เส้นทางหลักคือส่งลิงก์ GitHub ต้นทาง + คำขอภาษาธรรมดา ให้ AI อ่าน README เลือกวิธีติดตั้งเอง พร้อมตาราง repo 3 ตัวและสถานะตามเอกสารต้นทาง (Kokoro = ไลบรารี ไม่ใช่ MCP server) ตัดเงื่อนไขว่าต้องมี `labs/kokoro-web` / `labs/my-mcp-server` ก่อน
2. 4.2.1 / 4.2.2 เปลี่ยนพรอมป์ต์ 9 ขั้นเป็นคำขอสั้น ๆ พร้อมลิงก์ repo เหมือนกันทั้งสอง Host ต่างเฉพาะ Host ที่ให้ตั้งค่า พร้อมเหตุผลของการเขียนคำขอและเกณฑ์ผ่าน
3. 4.3.1–4.3.3 เปลี่ยนเป็นคำขอต่อเครื่องมือจาก repo ต้นทาง; 4.3.3 อธิบายชัดว่า Kokoro ไม่มี MCP server ต้องให้ AI เขียน wrapper เอง และให้ถามกลับถ้า AI อ้างว่ามี MCP server จาก repo
4. 4.3.4 ย้าย hello-lab / kokoro-tts / เว็บ Kokoro มาเป็น "แล็บต่อเนื่อง" ของบทที่ 6–7 ไม่ใช่ข้อบังคับเริ่มต้น (ไม่ลบตัวอย่างหรือคำสั่งทดสอบเดิม)
5. 4.4.1 (S5) ปรับให้ทดสอบเว็บสาธารณะ `https://www.python.org` ด้วย Playwright, ภาพ PNG จาก Excalidraw, ไฟล์เสียงจริงจาก Kokoro ส่วนแล็บของบทเรียนเป็นข้อเสริมที่ข้ามได้; 4.4.2 (S6) เป็นคำขอภาษาคน ถอนเฉพาะของบทเรียน
6. 4.5 คงตารางปัญหา/วิธีแก้ (ไม่มีตารางรอบ/ผล/เวลาติดตั้งกลับมา) ระบุว่า error มาจากการทดลองจริง 19 ก.ย. 2026 ด้วย Claude Code และยังไม่มีผลฝั่ง Codex
7. 4.6 ระบุชัดว่าเป็นส่วนอ้างอิงเสริม และเพิ่ม 4.6.9 เก็บพรอมป์ต์ติดตั้งฉบับละเอียดเดิม (ทั้ง Claude และ Codex) ไว้ครบตามเดิม
8. แก้ลิงก์/ข้อความอ้างอิงข้ามบท (ส่วนต้นบท, 5.1, 6.1, 7.1, 7.4, ภาคผนวก) ให้ตรงกับโครงใหม่
9. ซ่อมบรรทัด Markdown ที่เสียมาก่อนหน้า 3 จุด (`\1` ที่ทำให้ภาพ `img/d05-case1-excalidraw-flow.png` ไม่แสดง, ย่อหน้าในบท 7.4 และแถวตารางในภาคผนวก)

## สิ่งที่เปลี่ยนใน labs/prompts/setup-*.md
สร้างใหม่ให้ตรงกับ readme บทที่ 4 ทั้ง 8 ไฟล์ (S0 Claude / S0 Codex / S1–S4 / S5 / S6) พร้อมส่วน "ตรวจอย่างไรว่าทำงานสำเร็จ" และลิงก์ภายในที่ถูกต้องตาม path ของโฟลเดอร์ `labs/prompts`
ไฟล์ S0 ทั้งสองมีภาคผนวกเก็บพรอมป์ต์ฉบับละเอียดเดิมไว้ครบ

## การตรวจสอบ
- code fence: อ่านทุกไฟล์แล้วนับเปิด/ปิดครบคู่ (readme 96, prompts 2–8 ต่อไฟล์)
- ลิงก์ไฟล์ภายในทั้งหมดของ readme และ prompts: ตรวจการมีอยู่จริงของ path → ไม่พบลิงก์เสีย
- anchor ภายใน (`#ch1`…): ครบทุกตัวที่ถูกอ้าง
- ตาราง Markdown: ทุกหัวตารางมีบรรทัดคั่น
- `git diff --stat`: แก้เฉพาะ `03_MCP/readme.md` และ `03_MCP/labs/prompts/setup-*.md`

## ข้อจำกัด
- ไม่มีการรันติดตั้ง/ทดสอบใหม่ในรอบนี้ ตัวอย่างผลทั้งหมดในบทที่ 4 เขียนกำกับว่าเป็น Expected output
- ยังไม่มีผลรันจริงฝั่ง Codex (ติด auth ของ Codex default profile) หลักฐานภาพ/เสียง/สาย JSON-RPC ทั้งหมดยังเป็นของ Claude Code ตามเดิม ไม่ได้ดัดแปลง
- ข้อมูลจาก repo ต้นทางอ่านเมื่อ 20 กันยายน 2026 หาก README ต้นทางเปลี่ยน เอกสารระบุให้ยึด README เป็นหลัก
