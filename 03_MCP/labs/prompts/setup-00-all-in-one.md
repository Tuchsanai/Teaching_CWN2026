# Setup Prompt S0 (Claude Code) — ส่งลิงก์ repo ต้นทาง แล้วให้ AI ติดตั้งเอง

เปิด `claude` ในโฟลเดอร์ทำงาน แล้วพิมพ์/วางข้อความสั้น ๆ นี้ ไม่ต้องบอกคำสั่งติดตั้งให้ AI

```text
ช่วยติดตั้งเครื่องมือ MCP 3 ตัวนี้ให้ Claude Code บนเครื่องนี้ ให้ใช้งานได้จริง

1. Excalidraw MCP — https://github.com/yctimlin/mcp_excalidraw
2. Playwright MCP — https://github.com/microsoft/playwright-mcp
3. Kokoro TTS — https://github.com/hexgrad/kokoro

วิธีทำงาน: เปิดอ่าน README ของแต่ละ repo ก่อน สำรวจว่ามีวิธีติดตั้งและวิธีต่อกับ Host แบบใดบ้าง แล้วเลือกวิธีที่เหมาะกับเครื่องนี้และกับ Claude Code (เช่นเครื่องนี้มีจอหรือไม่ รันด้วยสิทธิ์อะไร Node/Python เวอร์ชันเท่าไร) ถ้า repo ไหนไม่ได้ให้ MCP server มา ให้บอกฉันก่อนว่าไม่มี แล้วเขียน MCP server ห่อความสามารถหลักของมันขึ้นมาเองอย่างง่าย
ตั้งค่าให้ Claude Code รู้จัก server ที่ได้ แล้วทดสอบว่าเรียก tool ได้จริง: Excalidraw ต้องวาดและส่งออกไฟล์ภาพได้, Playwright ต้องเปิดเว็บสาธารณะได้จริง, Kokoro ต้องได้ไฟล์เสียงที่เปิดฟังได้
สุดท้ายรายงานเป็นตาราง: ชื่อ server, วิธีติดตั้งที่เลือกและเหตุผล, คำสั่งที่รันจริง, ผลทดสอบ, ปัญหาที่เจอพร้อมข้อความ error จริง ห้ามแต่งผลลัพธ์ ถ้าข้อไหนยังไม่ได้ทดสอบให้เขียนว่า "ยังไม่ทดสอบ" ถ้าต้องใช้ sudo แล้วรันไม่ได้ ให้บอกคำสั่งที่ฉันต้องรันเองแล้วทำข้ออื่นต่อ
```

ทำไมคำขอถึงสั้นแบบนี้: (1) สิ่งที่เราสั่งคือ **เป้าหมายและเกณฑ์ผ่าน** ไม่ใช่ขั้นตอน เพราะขั้นตอนที่ถูกต้องอยู่ใน README ของ repo และเปลี่ยนตามเวอร์ชัน (2) บังคับให้ AI สำรวจเครื่องก่อนเลือกวิธี เพราะทางเลือกต่างกันตามเครื่อง เช่น repo ของ Excalidraw เสนอทั้ง agent skill/CLI และ MCP server (3) บอกล่วงหน้าว่า repo ที่ไม่มี MCP server ให้ **แจ้งก่อนแล้วค่อยห่อเอง** เพื่อไม่ให้ AI แต่งว่ามี MCP server สำเร็จรูปทั้งที่ไม่มี (4) กำหนดเกณฑ์เป็นผลลัพธ์ที่ตรวจได้ (ภาพ เว็บจริง ไฟล์เสียง) ไม่ใช่ "ลงเสร็จแล้ว"

**ตรวจอย่างไรว่าคำขอนี้ทำงานสำเร็จ**

**วิธีอ่านผล:** ตัวอย่างด้านล่างเป็น **ผลที่คาดหวัง (Expected output)** เพื่อใช้ตรวจงาน ไม่ใช่ผลรันใหม่หรือข้อความที่ Host ต้องตอบตรงทุกตัวอักษร ชื่อ server ค่า path และเวลาจะแตกต่างกันได้ ต้องมีผลจาก tool หรือไฟล์จริงรองรับคำว่า “ผ่าน”

**ทดสอบหลังวาง S0:** เมื่อการติดตั้งจบ ให้พิมพ์ `/exit` เปิด Claude Code เป็น session ใหม่ (MCP server ที่เพิ่งลงทะเบียนโหลดตอนเริ่ม session เท่านั้น) แล้ววาง S5 ในข้อ 4.4.1

**ตัวอย่างผลที่ควรเห็น**

```text
การตั้งค่า: claude mcp list แสดง server ของ Excalidraw และ Playwright เป็น Connected
Excalidraw: วาดกล่องบน canvas แล้ว export เป็น PNG ที่เปิดดูได้
Playwright: เปิด https://www.python.org ได้จริง มี snapshot/screenshot ของหน้าเว็บ
Kokoro: repo เป็นไลบรารี ไม่มี MCP server จึงเขียน wrapper ขึ้นมา แล้วสร้าง .wav ที่เปิดฟังได้
```

**ผ่านเมื่อ:** เห็นภาพจาก Excalidraw, หน้าเว็บจริงจาก Playwright และไฟล์เสียงที่เปิดฟังได้จาก Kokoro ครบสามอย่าง การเห็นชื่อ server ในรายการอย่างเดียวยังไม่พอ ถ้าติดตั้งเสร็จแต่ยังไม่ได้ใช้ S5 ให้ระบุว่า “ติดตั้งแล้ว / ยังไม่ได้ทดสอบใช้งาน”

---

เนื้อหาไฟล์นี้ตรงกับ readme.md บทที่ 4 (ฉบับแก้ 20 กันยายน 2026) เส้นทางหลักคือส่งลิงก์ repo ต้นทางพร้อมคำขอภาษาธรรมดา แล้วให้ AI อ่าน README เลือกวิธีติดตั้งเอง พรอมป์ต์ติดตั้งฉบับละเอียดของเดิมย้ายไปเป็นข้อมูลอ้างอิงใน readme.md ข้อ 4.6.9

## ภาคผนวก: พรอมป์ต์ติดตั้งฉบับละเอียด (ฉบับเดิม 19 กันยายน 2026)

เก็บไว้เป็นข้อมูลอ้างอิงเท่านั้น ไม่ใช่เส้นทางการเรียนหลัก ฉบับนี้สั่งขั้นตอนให้ AI ครบทุกข้อและอ้างถึงโค้ดแล็บของบทเรียน (`labs/kokoro-web`, `labs/my-mcp-server`) หลักฐานใน `lab-results/setup-prompt/run-2026-09-19-072524/` เกิดจากพรอมป์ต์ชุดนี้

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
