# LAB 0 · ผลการรัน (ตรวจเครื่องให้พร้อม)

- เวลาเริ่ม: 2026-10-10 17:41:08 (+07)
- เวลาจบ: 2026-10-10 17:43 (+07)
- เวลาที่ใช้: ประมาณ 2 นาที
- โหมด: อ่านอย่างเดียว ไม่ติดตั้งและไม่แก้อะไร ทุกค่ามาจากคำสั่งที่รันจริง

## คำตอบสรุปที่แสดงในแชท

| รายการ | ผล (จากคำสั่งจริง) | พร้อมไหม | ถ้าไม่พร้อมต้องทำอะไร |
|---|---|---|---|
| Docker Desktop (`docker version`) | Client 29.5.2 / Server: Docker Desktop 4.75.0, Engine 29.5.2, context `desktop-linux` | ✅ พร้อม | — |
| Docker Compose (`docker compose version`) | Docker Compose version v5.1.4 | ✅ พร้อม | — |
| Node.js (`node -v`) | v26.7.0 (ต้อง ≥ 20) | ✅ พร้อม | — |
| npm (`npm -v`) | 12.2.0 | ✅ พร้อม | — |
| ffmpeg (`ffmpeg -version`) | 8.0.1-full_build-www.gyan.dev (มี libx264, libwebp ใช้ทำ GIF/MP4 ได้) | ✅ พร้อม | — |
| Playwright MCP (`claude mcp list`) | `playwright: npx -y @playwright/mcp@latest --extension - ✔ Connected` | ✅ พร้อม | — (เป็นโหมด `--extension` ที่เกาะ Chrome ตัวจริง ต้องเปิด Chrome พร้อมส่วนขยาย Playwright MCP Bridge ไว้) |
| Codex CLI (`codex --version`, ไม่บังคับ) | codex-cli 0.161.0 | ✅ มี | — (ใช้ Codex สร้างรูปในเว็บได้) |
| พอร์ต 3000 (เว็บ) | ว่าง ไม่มีโปรแกรม LISTEN (`Get-NetTCPConnection` และ `netstat` ไม่พบ) | ✅ ว่าง | — |
| พอร์ต 5433 (ฐานข้อมูล) | ว่าง ไม่มีโปรแกรม LISTEN | ✅ ว่าง | — |

**สรุป: พร้อม 9/9 รายการ** เริ่ม LAB 1 ได้เลย

container ที่รันอยู่ตอนนี้ (`docker ps`) มี 2 ตัว ใช้พอร์ตคนละชุดกับบทนี้ จึงไม่ชนกัน:
- `multi-account-devtool` → 2380, 8886
- `deep_vision_5090_vllm` → 22022, 8650

ไม่พบ container ชื่อ sabai-web, sabai-db หรือ petshop (`docker ps -a` ก็ไม่มี)

## ตัวเลขสำคัญ
- จำนวนรายการที่ตรวจ 9 รายการ (นับ Docker/Compose, Node/npm และพอร์ตแยกกัน) พร้อม 9 ไม่พร้อม 0
- MCP server ใน `claude mcp list` ทั้งหมด 18 ตัว: Connected 5 ตัว (playwright, Claude Docs, Google Calendar, Gmail, Google Drive), Needs authentication 12 ตัว, Failed 1 ตัว (kokoro-tts) ทั้งหมดนี้ไม่เกี่ยวกับบทนี้ ยกเว้น playwright
- container ที่รันอยู่ 2 ตัว และไม่มีตัวไหนใช้พอร์ต 3000 หรือ 5433

## ตัวอย่างแถวเด่น (สำหรับ README)
| รายการ | ผล | พร้อมไหม | ถ้าไม่พร้อมต้องทำอะไร |
|---|---|---|---|
| Node.js | v26.7.0 (≥20) | ✅ | — |
| Playwright MCP | ✔ Connected (`--extension`) | ✅ | — |
| Codex CLI (ไม่บังคับ) | codex-cli 0.161.0 | ✅ | ถ้าไม่มี Claude จะวาดรูปเองเป็น SVG |
| พอร์ต 5433 | ว่าง | ✅ | ถ้าไม่ว่าง ให้ดูชื่อ container ด้วย `docker ps` แล้วสั่ง stop |

## ข้อสังเกต 👀
- 👀 `claude mcp list` ใช้เวลาหลายวินาที เพราะต้องเช็ก server ทุกตัว ถ้ามี server ที่ต่อไม่ติด (เช่น kokoro-tts) จะช้าลงอีก ไม่ต้องตกใจ ดูแค่บรรทัด `playwright`
- 👀 Playwright MCP ขึ้น Connected แต่ตั้งไว้เป็นโหมด `--extension` ซึ่งแปลว่าจะเกาะ Chrome ตัวจริงของผู้ใช้ (cookie และแท็บจริง) ตอนทดสอบควรระวังเรื่องนี้
- 👀 บน Windows การเช็กพอร์ตด้วย `Get-NetTCPConnection -LocalPort 3000 -State Listen` (PowerShell) หรือ `netstat -ano | findstr :3000` จะได้ PID มาด้วย ส่วน `docker ps` จะบอกว่า container ไหน map พอร์ตไว้
- 👀 พอร์ตฐานข้อมูลเป็น 5433 ไม่ใช่ 5432 ที่เป็นค่าปกติของ Postgres จะได้ไม่ชนกับ Postgres ที่อาจติดตั้งไว้ในเครื่องอยู่แล้ว
- ปัญหาที่เจอ: ไม่มี

## ข้อเสนอแก้พรอมต์
1. ข้อ 6: ควรระบุคำสั่งเช็กพอร์ตแยกตามระบบปฏิบัติการ เช่น "Windows ใช้ `netstat -ano | findstr :3000`, macOS/Linux ใช้ `lsof -i :3000`" และให้ "เช็ก `docker ps -a` ด้วย" เพราะ container ที่หยุดอยู่อาจกลับมาจองพอร์ตทีหลังได้
2. ข้อ 4: ควรเพิ่มว่า "ถ้า playwright ตั้งเป็นโหมด `--extension` ให้บอกด้วยว่าต้องเปิด Chrome และส่วนขยาย Playwright MCP Bridge ไว้" เพราะ Connected อย่างเดียวไม่ได้รับประกันว่าจะสั่งเบราว์เซอร์ได้
3. ข้อ 2: เขียนว่า "ต้อง 20 ขึ้นไป" ชัดแล้ว แต่ควรแนะนำให้ใช้รุ่น LTS (20/22/24) ด้วย ถ้าผู้เรียนใช้รุ่นใหม่มาก (เช่น v26) อาจเจอ native module บางตัวที่ยังไม่รองรับ

## ภาพหน้าจอ
- `../design/shots/lab0-checklist.png` (headless 1280x800): ตารางสรุปผลตรวจเครื่อง 9/9 รายการ ไว้ใส่ README ตรงหัวข้อ LAB 0 (สร้างด้วยสคริปต์ `../tools/lab0/shot.js` ที่ render ตารางจากผลจริง)
