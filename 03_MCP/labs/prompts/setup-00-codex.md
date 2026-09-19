# Setup Prompt S0 — สำหรับ Codex CLI

#### 4.2.2 สำหรับ Codex CLI

เปิด `codex` จากโฟลเดอร์ `03_MCP` แล้วคัดลอกทั้งบล็อกไปวาง ไม่ต้องแปลงคำสั่งของ Claude Code เอง ดูขั้นตอนและคำสั่งประกอบใน [บทที่ 4](../../readme.md#ch4)

> ตัวอย่างนี้ตรวจรูปแบบคำสั่งกับ `codex mcp --help`, `codex mcp add --help` บน Remote และ [เอกสาร MCP ของ OpenAI](https://developers.openai.com/codex/mcp) แล้ว แต่ยังไม่ได้รันติดตั้งและทดสอบผ่าน Codex ครบชุด จึงไม่ใช่ผลทดลองที่ยืนยันแล้ว

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

**ตรวจอย่างไรว่าพรอมป์ต์นี้ทำงานสำเร็จ**

**วิธีอ่านผล:** ตัวอย่างด้านล่างเป็น **ผลที่คาดหวัง (Expected output)** เพื่อใช้ตรวจงาน ไม่ใช่ผลรันใหม่หรือข้อความที่ Host ต้องตอบตรงทุกตัวอักษร ค่า path ชื่อไฟล์ และเวลาจะแตกต่างกันได้ ต้องมีผลจาก tool หรือไฟล์จริงรองรับคำว่า “ผ่าน”

**ทดสอบหลังวาง S0:** เปิด Codex CLI เป็น session ใหม่ ดู server ด้วย `/mcp` แล้ววาง S5 ในข้อ 4.4.1

**ตัวอย่างผลที่ควรเห็น**

```text
การตั้งค่า: codex mcp list มี server ของบทเรียนครบ 4 ตัว
hello-lab: add(17, 25) → 42
Excalidraw: ได้ไฟล์ PNG ที่เปิดดูได้
Playwright: หน้าเว็บแสดง “สร้างเสียงสำเร็จ” หลังกรอกและกด Speak
kokoro-tts: ได้ไฟล์ .wav ที่เปิดได้ และความยาวมากกว่า 0
รายงานติดตั้ง: labs/setup-report-codex.md
```

**ผ่านเมื่อ:** เรียก tool จริงครบตาม S5 ไม่ใช่แค่มีชื่อใน `codex mcp list` ถ้า session ไม่เห็น tool ให้ตรวจ path ด้วย `codex mcp get <ชื่อ server>` แล้วเปิด session ใหม่ก่อนทดสอบซ้ำ


