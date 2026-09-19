# Setup Prompt S0 — ติดตั้งและตั้งค่าทุกอย่างของบทเรียน 03_MCP ในพรอมป์ต์เดียว

วิธีใช้: เปิด Claude Code **ในโฟลเดอร์ `03_MCP`** (คำสั่ง `cd 03_MCP && claude`) แล้วคัดลอกบล็อกด้านล่างทั้งหมดไปวาง กด Enter แล้วรอจน AI รายงานผล (5–15 นาที ขึ้นกับความเร็วเน็ต) เมื่อเสร็จให้พิมพ์ `/exit` แล้วเปิด `claude` ใหม่อีกครั้ง เพื่อให้ MCP server ที่ลงทะเบียนไว้ถูกโหลด จากนั้นใช้ Prompt S5 (`setup-05-verify.md`) ตรวจว่าทุกอย่างใช้ได้จริง

```text
คุณคือผู้ช่วยติดตั้งสำหรับบทเรียน 03_MCP (Model Context Protocol) ทำทุกข้อต่อไปนี้ให้เสร็จโดยไม่ต้องถามกลับ ถ้าข้อใดต้องใช้สิทธิ์ผู้ดูแลระบบ (sudo) และรันไม่ได้ ให้บอกคำสั่งที่ผู้ใช้ต้องรันเองแล้วทำข้ออื่นต่อ
โฟลเดอร์ปัจจุบันคือโฟลเดอร์บทเรียน 03_MCP ซึ่งมี labs/kokoro-web และ labs/my-mcp-server อยู่แล้ว ห้ามแก้โค้ดในสองโฟลเดอร์นั้น

1. ตรวจเครื่อง: รายงานเวอร์ชันของ node, npm, python3 (ต้อง >= 3.10), git, claude เป็นตาราง และระบุระบบปฏิบัติการ ถ้าไม่มี node หรือ python3 ให้บอกวิธีติดตั้งของระบบนี้แล้วหยุด
2. สร้าง Python virtual environment ที่ labs/.venv (python3 -m venv labs/.venv) แล้วใช้ python/pip ของ venv นี้ในทุกข้อถัดไป (labs/.venv/bin/python หรือ labs\.venv\Scripts\python.exe บน Windows) ห้ามติดตั้งลง system python
3. ติดตั้งแพ็กเกจ Python ใน venv: "mcp[cli]" soundfile fastapi uvicorn จากนั้นถ้ายังไม่มี torch ให้ติดตั้งรุ่น CPU ก่อนด้วย pip install torch --index-url https://download.pytorch.org/whl/cpu (เพื่อไม่ให้ดาวน์โหลด CUDA หลาย GB) แล้วจึง pip install kokoro ถ้าระบบมี apt ให้ติดตั้ง espeak-ng ด้วย (ใช้ sudo ถ้าจำเป็น)
4. ติดตั้ง MCP server แบบ Node ให้ใช้ได้ทั่วเครื่อง: npm install -g mcp-excalidraw-server @playwright/mcp แล้วดาวน์โหลดเบราว์เซอร์ให้ Playwright ด้วย npx playwright install chromium (บน Linux ให้รัน npx playwright install-deps chromium ด้วย)
5. ลงทะเบียน MCP server กับ Claude Code ระดับผู้ใช้ (--scope user) 4 ตัว โดยใช้ path แบบเต็มทุกตัว:
   - excalidraw: command mcp-excalidraw-server (ไม่ต้องใส่ argument)
   - playwright: command playwright-mcp argument --browser chromium (ใช้ chromium ที่เพิ่งติดตั้ง ไม่ใช่ Google Chrome) ถ้าเครื่องนี้ไม่มีจอแสดงผล (เช่น server หรือ container) ให้เพิ่ม --headless และถ้ารันเป็น root ให้เพิ่ม --no-sandbox ด้วย
   - hello-lab: command <python ของ venv> argument <path เต็มของ labs/my-mcp-server/hello_server.py>
   - kokoro-tts: command <python ของ venv> argument <path เต็มของ labs/my-mcp-server/tts_server.py> พร้อม env KOKORO_DEVICE=cpu
   ถ้ามีชื่อซ้ำอยู่แล้วให้ claude mcp remove ชื่อนั้นก่อน
6. เริ่มเว็บทดลอง Kokoro: ตั้ง PYTHON=<python ของ venv> แล้วรัน labs/kokoro-web/run.sh จากนั้น curl http://127.0.0.1:8765/api/health จนได้ "ok":true (รอได้ไม่เกิน 60 วินาที) แล้วลอง curl -X POST http://127.0.0.1:8765/api/tts -H "Content-Type: application/json" -d '{"text":"Setup test from prompt.","voice":"af_heart"}' บันทึกเวลาที่ใช้ (ครั้งแรกจะช้าเพราะโหลดโมเดล)
7. ทดสอบ server ของบทเรียนโดยไม่ใช้ LLM: <python ของ venv> labs/my-mcp-server/client_test.py --server hello ต้องเห็น tools/list และผล add(17, 25) = 42
8. ตรวจสอบสุดท้ายด้วย claude mcp list ต้องเห็น excalidraw, playwright, hello-lab, kokoro-tts และสถานะเป็น Connected ทั้งหมด ถ้าตัวใดไม่ Connected ให้อ่าน error แล้วแก้ (เช่น path ผิด, แพ็กเกจยังไม่ติดตั้ง) จนผ่าน
9. เขียนไฟล์ labs/setup-report.md ภาษาไทย ประกอบด้วย ตารางเวอร์ชัน, คำสั่งที่รันทั้งหมดตามลำดับ, ผล claude mcp list, เวลาที่ใช้แต่ละขั้น, และปัญหาที่พบพร้อมข้อความ error จริงและวิธีแก้ ห้ามแต่งผลลัพธ์ ถ้าข้อใดไม่ผ่านให้ระบุชัดเจน
สุดท้ายสรุปให้ผู้ใช้ทราบว่าต้องพิมพ์ /exit แล้วเปิด claude ใหม่เพื่อใช้ MCP server ที่ลงทะเบียน และถ้าเครื่องมีจอ ให้เปิด http://127.0.0.1:3000 ในเบราว์เซอร์เมื่อจะใช้ Excalidraw (ถ้าไม่มีจอ ให้ใช้ Prompt S5 เปิดผ่าน Playwright แทน)
```

หมายเหตุ: ถ้าใช้ Codex CLI ให้แทนข้อ 5 ด้วยการเขียน `[mcp_servers.*]` ลง `~/.codex/config.toml` ตามตัวอย่างใน `labs/my-mcp-server/codex-config-snippet.toml` แล้วตรวจด้วย `codex mcp list` (**แนวทาง — ยังไม่ได้ทดลองกับ Codex**)
