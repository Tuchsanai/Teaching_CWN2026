# Setup Prompt S0 (Codex CLI) — ส่งลิงก์ repo ต้นทาง แล้วให้ AI ติดตั้งเอง

เปิด `codex` ในโฟลเดอร์ทำงาน แล้ววางข้อความนี้ ใช้ **repo ต้นทางชุดเดียวกับฉบับ Claude Code** ([`setup-00-all-in-one.md`](setup-00-all-in-one.md)) ต่างกันเฉพาะ Host ที่ให้ตั้งค่า

> ขอบเขตตามจริง: รอบนี้เป็นการแก้เอกสารเท่านั้น ยังไม่มีผลรันจริงฝั่ง Codex เพราะการทดสอบครั้งก่อนติดปัญหาการยืนยันตัวตนของ Codex default profile หลักฐานภาพ/เสียง/สาย JSON-RPC ทั้งหมดในบทเรียนมาจาก Claude Code อย่าอ่านว่าเป็นผลของ Codex

```text
ช่วยติดตั้งเครื่องมือ MCP 3 ตัวนี้ให้ Codex CLI บนเครื่องนี้ ให้ใช้งานได้จริง

1. Excalidraw MCP — https://github.com/yctimlin/mcp_excalidraw
2. Playwright MCP — https://github.com/microsoft/playwright-mcp
3. Kokoro TTS — https://github.com/hexgrad/kokoro

วิธีทำงาน: เปิดอ่าน README ของแต่ละ repo ก่อน สำรวจว่ามีวิธีติดตั้งและวิธีต่อกับ Host แบบใดบ้าง (README ของสองตัวแรกมีส่วนสำหรับ Codex โดยเฉพาะ) แล้วเลือกวิธีที่เหมาะกับเครื่องนี้ ถ้า repo ไหนไม่ได้ให้ MCP server มา ให้บอกฉันก่อนว่าไม่มี แล้วเขียน MCP server ห่อความสามารถหลักของมันขึ้นมาเองอย่างง่าย
ตั้งค่าให้ Codex รู้จัก server ที่ได้ โดยแก้เฉพาะรายการของบทเรียนนี้ ห้ามแตะ server อื่นที่มีอยู่เดิม แล้วทดสอบว่าเรียก tool ได้จริง: Excalidraw ต้องวาดและส่งออกไฟล์ภาพได้, Playwright ต้องเปิดเว็บสาธารณะได้จริง, Kokoro ต้องได้ไฟล์เสียงที่เปิดฟังได้
สุดท้ายรายงานเป็นตาราง: ชื่อ server, วิธีติดตั้งที่เลือกและเหตุผล, คำสั่งที่รันจริง, ผลทดสอบ, ปัญหาที่เจอพร้อมข้อความ error จริง ห้ามแต่งผลลัพธ์ รายการ server ที่ตั้งค่าไว้ยังไม่ถือว่าทดสอบผ่าน ต้องเรียก tool จริงใน session ใหม่
```

**ตรวจอย่างไรว่าคำขอนี้ทำงานสำเร็จ**

**วิธีอ่านผล:** ตัวอย่างด้านล่างเป็น **ผลที่คาดหวัง (Expected output)** เพื่อใช้ตรวจงาน ไม่ใช่ผลรันใหม่หรือข้อความที่ Host ต้องตอบตรงทุกตัวอักษร ชื่อ server ค่า path และเวลาจะแตกต่างกันได้ ต้องมีผลจาก tool หรือไฟล์จริงรองรับคำว่า “ผ่าน”

**ทดสอบหลังวาง S0:** เปิด Codex CLI เป็น session ใหม่ ดู server ที่ใช้งานอยู่ด้วย `/mcp` แล้ววาง S5 ในข้อ 4.4.1

**ตัวอย่างผลที่ควรเห็น**

```text
การตั้งค่า: codex mcp list มี server ของบทเรียนครบตามที่ตั้งค่า
Excalidraw: ได้ไฟล์ PNG ที่เปิดดูได้
Playwright: เปิด https://www.python.org แล้วรายงานชื่อหน้าและ snapshot ได้
Kokoro: ได้ไฟล์ .wav ที่เปิดฟังได้ ความยาวมากกว่า 0
```

**ผ่านเมื่อ:** เรียก tool จริงครบตาม S5 ไม่ใช่แค่มีชื่อใน `codex mcp list` ถ้า session ไม่เห็น tool ให้ตรวจค่าที่ตั้งไว้ด้วย `codex mcp get <ชื่อ server>` แล้วเปิด session ใหม่ก่อนทดสอบซ้ำ

---

เนื้อหาไฟล์นี้ตรงกับ readme.md บทที่ 4 (ฉบับแก้ 20 กันยายน 2026) เส้นทางหลักคือส่งลิงก์ repo ต้นทางพร้อมคำขอภาษาธรรมดา แล้วให้ AI อ่าน README เลือกวิธีติดตั้งเอง พรอมป์ต์ติดตั้งฉบับละเอียดของเดิมย้ายไปเป็นข้อมูลอ้างอิงใน readme.md ข้อ 4.6.9

## ภาคผนวก: พรอมป์ต์ติดตั้งฉบับละเอียด (ฉบับเดิม 19 กันยายน 2026)

เก็บไว้เป็นข้อมูลอ้างอิงเท่านั้น ไม่ใช่เส้นทางการเรียนหลัก ฉบับนี้สั่งขั้นตอนให้ AI ครบทุกข้อและอ้างถึงโค้ดแล็บของบทเรียน (`labs/kokoro-web`, `labs/my-mcp-server`) หลักฐานใน `lab-results/setup-prompt/run-2026-09-19-072524/` เกิดจากพรอมป์ต์ชุดนี้

```text
คุณคือผู้ช่วยติดตั้งสำหรับบทเรียน 03_MCP (Model Context Protocol) ทำทุกข้อต่อไปนี้ให้เสร็จโดยไม่ต้องถามกลับ ถ้าข้อใดต้องใช้สิทธิ์ผู้ดูแลระบบ (sudo) และรันไม่ได้ ให้บอกคำสั่งที่ผู้ใช้ต้องรันเองแล้วทำข้ออื่นต่อ
โฟลเดอร์ปัจจุบันคือโฟลเดอร์บทเรียน 03_MCP ซึ่งมี labs/kokoro-web และ labs/my-mcp-server อยู่แล้ว ห้ามแก้โค้ดในสองโฟลเดอร์นั้น

1. ตรวจเครื่อง: รายงานเวอร์ชันของ node, npm, python3 (ต้อง >= 3.10), git, codex เป็นตาราง และระบุระบบปฏิบัติการ ถ้าไม่มี node หรือ python3 ให้บอกวิธีติดตั้งของระบบนี้แล้วหยุด
2. สร้าง Python virtual environment ที่ labs/.venv (python3 -m venv labs/.venv) แล้วใช้ python/pip ของ venv นี้ในทุกข้อถัดไป (labs/.venv/bin/python หรือ labs\.venv\Scripts\python.exe บน Windows) ห้ามติดตั้งลง system python
3. ติดตั้งแพ็กเกจ Python ใน venv: "mcp[cli]" soundfile fastapi uvicorn จากนั้นถ้ายังไม่มี torch ให้ติดตั้งรุ่น CPU ก่อนด้วย pip install torch --index-url https://download.pytorch.org/whl/cpu (เพื่อไม่ให้ดาวน์โหลด CUDA หลาย GB) แล้วจึง pip install kokoro ถ้าระบบมี apt ให้ติดตั้ง espeak-ng ด้วย (ใช้ sudo ถ้าจำเป็น)
4. ติดตั้ง MCP server แบบ Node ให้ใช้ได้ทั่วเครื่อง: npm install -g mcp-excalidraw-server @playwright/mcp แล้วดาวน์โหลดเบราว์เซอร์ให้ Playwright ด้วย npx playwright install chromium (บน Linux ให้รัน npx playwright install-deps chromium ด้วย)
5. ลงทะเบียน MCP server กับ Codex CLI ด้วย codex mcp add 4 ตัว โดยใช้ path แบบเต็มทุกตัว:
   - excalidraw: command mcp-excalidraw-server (ไม่ต้องใส่ argument)
   - playwright: command playwright-mcp argument --browser chromium (ใช้ chromium ที่เพิ่งติดตั้ง ไม่ใช่ Google Chrome) ถ้าเครื่องนี้ไม่มีจอแสดงผล (เช่น server หรือ container) ให้เพิ่ม --headless และถ้ารันเป็น root ให้เพิ่ม --no-sandbox ด้วย
   - hello-lab: command <python ของ venv> argument <path เต็มของ labs/my-mcp-server/hello_server.py>
   - kokoro-tts: command <python ของ venv> argument <path เต็มของ labs/my-mcp-server/tts_server.py> พร้อม env KOKORO_DEVICE=cpu
   ตรวจ codex mcp get ก่อน ถ้าค่าตรงแล้วให้ใช้ของเดิม ถ้าต้องเปลี่ยนให้สำรองเฉพาะค่าของ server นั้นแล้วใช้ codex mcp remove และเพิ่มใหม่ ห้ามแก้ server อื่น
6. เริ่มเว็บทดลอง Kokoro: ตั้ง PYTHON=<python ของ venv> แล้วรัน labs/kokoro-web/run.sh จากนั้น curl http://127.0.0.1:8765/api/health จนได้ "ok":true (รอได้ไม่เกิน 60 วินาที) แล้วลอง curl -X POST http://127.0.0.1:8765/api/tts -H "Content-Type: application/json" -d '{"text":"Setup test from prompt.","voice":"af_heart"}' บันทึกเวลาที่ใช้ (ครั้งแรกจะช้าเพราะโหลดโมเดล)
7. ทดสอบ server ของบทเรียนโดยไม่ใช้ LLM: <python ของ venv> labs/my-mcp-server/client_test.py --server hello ต้องเห็น tools/list และผล add(17, 25) = 42
8. ตรวจ codex mcp list ว่ามีทั้ง 4 server และ codex mcp get ทีละชื่อว่าคำสั่ง path และ env ถูกต้อง รายการนี้ยืนยันการตั้งค่าเท่านั้น ยังไม่ถือว่าทดสอบ tool ผ่าน ให้ทดสอบ tool จริงด้วย S5 ใน Codex session ใหม่
9. เขียนไฟล์ labs/setup-report-codex.md ภาษาไทย ประกอบด้วย ตารางเวอร์ชัน, คำสั่งที่รันทั้งหมดตามลำดับ, ผล codex mcp list, เวลาที่ใช้แต่ละขั้น, และปัญหาที่พบพร้อมข้อความ error จริงและวิธีแก้ ห้ามแต่งผลลัพธ์ ถ้าข้อใดไม่ผ่านให้ระบุชัดเจน
สุดท้ายสรุปให้ผู้ใช้เปิด codex เป็น session ใหม่ ใช้ /mcp ดู server ที่ใช้งานอยู่ แล้ววาง Prompt S5 เพื่อทดสอบจริง ถ้าไม่มีจอให้เปิด canvas ผ่าน Playwright ตาม S5 ห้ามรายงานว่าการทดสอบผ่านถ้ายังไม่ได้เรียก tool
```
