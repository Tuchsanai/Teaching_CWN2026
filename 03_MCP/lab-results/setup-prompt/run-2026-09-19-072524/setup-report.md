# รายงานการติดตั้งแล็บ 03_MCP (Model Context Protocol)

วันที่ทำการติดตั้ง: 2026-09-19
ระบบปฏิบัติการ: Ubuntu 24.04.4 LTS (Noble Numbat), kernel `6.6.87.2-microsoft-standard-WSL2` (x86_64) — รันเป็น root ในคอนเทนเนอร์/WSL2 ไม่มีจอแสดงผล (`$DISPLAY` ว่างเปล่า)

## 1. ตารางเวอร์ชันเครื่องมือ

| เครื่องมือ | เวอร์ชันที่พบ | หมายเหตุ |
|---|---|---|
| node | v22.23.1 | ผ่านเกณฑ์ |
| npm | 12.0.1 | ผ่านเกณฑ์ |
| python3 (system) | 3.12.3 | ผ่านเกณฑ์ (>= 3.10) |
| git | 2.54.0 | ผ่านเกณฑ์ |
| claude (Claude Code CLI) | 2.1.278 | ผ่านเกณฑ์ |
| python (venv `labs/.venv`) | 3.12.3 | สร้างใหม่จาก system python3 |

แพ็กเกจ Python ที่ติดตั้งใน `labs/.venv` (เวอร์ชันสุดท้าย):

| แพ็กเกจ | เวอร์ชัน |
|---|---|
| mcp[cli] | 2.2.0 |
| soundfile | 0.14.0 |
| fastapi | 0.141.1 |
| uvicorn | 0.53.0 |
| torch (CPU build) | 2.14.0+cpu |
| kokoro | 0.9.4 |

แพ็กเกจ Node ที่ติดตั้งแบบ global:

| แพ็กเกจ | เวอร์ชัน |
|---|---|
| mcp-excalidraw-server | 2.0.0 |
| @playwright/mcp | 0.0.82 |
| playwright (browser CLI ที่ @playwright/mcp พึ่งพา) | 1.63.0 |

ระบบมี apt และติดตั้ง `espeak-ng` สำเร็จ (เป็น dependency ของ kokoro/misaki สำหรับ phonemizer)

## 2. คำสั่งที่รันทั้งหมด (ตามลำดับ)

```bash
# 1) ตรวจเครื่อง
node --version; npm --version; python3 --version; git --version; claude --version

# 2) สร้าง venv
python3 -m venv labs/.venv

# 3) ติดตั้งแพ็กเกจ python
labs/.venv/bin/pip install --upgrade pip
labs/.venv/bin/pip install "mcp[cli]" soundfile fastapi uvicorn
labs/.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
labs/.venv/bin/pip install kokoro
apt-get update -qq && apt-get install -y espeak-ng -qq

# 4) ติดตั้ง MCP server แบบ node (global) + browser ของ playwright
npm install -g mcp-excalidraw-server @playwright/mcp
npx playwright install chromium
npx playwright install-deps chromium   # ติดตั้ง shared libs ที่ chromium ต้องใช้บน Linux

# 5) ลงทะเบียน MCP server กับ claude (--scope user)
claude mcp add excalidraw --scope user -- mcp-excalidraw-server
claude mcp add playwright --scope user -- playwright-mcp --headless
claude mcp add hello-lab --scope user -- /root/03_MCP/labs/.venv/bin/python /root/03_MCP/labs/my-mcp-server/hello_server.py
claude mcp add kokoro-tts --scope user --env KOKORO_DEVICE=cpu -- /root/03_MCP/labs/.venv/bin/python /root/03_MCP/labs/my-mcp-server/tts_server.py

# 6) เริ่มเว็บทดลอง Kokoro
PYTHON=/root/03_MCP/labs/.venv/bin/python labs/kokoro-web/run.sh
curl -s http://127.0.0.1:8765/api/health
curl -s -X POST http://127.0.0.1:8765/api/tts -H "Content-Type: application/json" \
  -d '{"text":"Setup test from prompt.","voice":"af_heart"}'

# 7) ทดสอบ hello-lab server โดยไม่ใช้ LLM
/root/03_MCP/labs/.venv/bin/python labs/my-mcp-server/client_test.py --server hello

# 8) ตรวจสอบสุดท้าย
claude mcp list
```

หมายเหตุ: ไม่มีขั้นตอนใดต้องใช้ `sudo` เพราะ session นี้รันเป็น `root` อยู่แล้ว ผู้ใช้ที่รันเป็น non-root user ทั่วไปให้เติม `sudo` หน้าเฉพาะคำสั่ง `apt-get` และ `npx playwright install-deps` เท่านั้น

## 3. ผล `claude mcp list` (สุดท้าย)

```
Checking MCP server health…

claude.ai Claude Docs: https://api.anthropic.com/v1/pages/mcp - ✔ Connected
claude.ai Canva: https://mcp.canva.com/mcp - ✔ Connected
claude.ai Google Calendar: https://calendarmcp.googleapis.com/mcp/v1 - ✔ Connected
claude.ai Google Drive: https://drivemcp.googleapis.com/mcp/v1 - ✔ Connected
claude.ai Gmail: https://gmailmcp.googleapis.com/mcp/v1 - ✔ Connected
excalidraw: mcp-excalidraw-server  - ✔ Connected
playwright: playwright-mcp --headless - ✔ Connected
hello-lab: /root/03_MCP/labs/.venv/bin/python /root/03_MCP/labs/my-mcp-server/hello_server.py - ✔ Connected
kokoro-tts: /root/03_MCP/labs/.venv/bin/python /root/03_MCP/labs/my-mcp-server/tts_server.py - ✔ Connected
```

**สถานะ: ผ่านทั้ง 4 ตัวที่ต้องการ** — excalidraw, playwright, hello-lab, kokoro-tts ทุกตัวขึ้น `✔ Connected` (มี MCP server อื่นของ claude.ai ที่ลงทะเบียนไว้ล่วงหน้าอยู่แล้วในเครื่องนี้ด้วย ไม่เกี่ยวข้องกับแล็บนี้ ไม่ได้แก้ไข)

หมายเหตุการตั้งค่า `playwright`: เครื่องนี้ไม่มีจอแสดงผล (`$DISPLAY` ว่างเปล่า, รันในคอนเทนเนอร์/WSL2 แบบ headless) จึงลงทะเบียนพร้อม argument `--headless` ตามเงื่อนไขของโจทย์

## 4. เวลาที่ใช้แต่ละขั้นตอน

| ขั้นตอน | เวลาที่ใช้ |
|---|---|
| `npm install -g mcp-excalidraw-server @playwright/mcp` | ~53 วินาที |
| `pip install torch --index-url .../cpu` | 25.7 วินาที |
| `pip install kokoro` | 22.6 วินาที |
| `npx playwright install chromium` (ดาวน์โหลด chromium + headless shell + ffmpeg) | 29.5 วินาที |
| `npx playwright install-deps chromium` | 14.7 วินาที |
| เริ่ม kokoro-web แล้วรอ `/api/health` ตอบ `"ok":true` | < 1 วินาที (ตอบทันที เพราะโมเดลยังไม่โหลดจนกว่าจะเรียก `/api/tts` ครั้งแรก — `model_loaded:false` ตอน health check) |
| เรียก `/api/tts` ครั้งแรก (โหลดโมเดล Kokoro-82M + สังเคราะห์เสียง) | `gen_ms: 3148` (≈3.15 วินาที) ได้ไฟล์ `20260919-143110-ce08eb78.wav` ยาว 1.93 วินาที, sample_rate 24000 |
| `client_test.py --server hello` (ครบทุก tools/resources/prompts) | 0.96 วินาที |

## 5. ปัญหาที่พบระหว่างติดตั้ง

**ไม่พบปัญหา** — ทุกคำสั่งรันผ่านในครั้งแรกโดยไม่มี error เนื่องจาก:
- ระบบนี้รันเป็น `root` อยู่แล้ว จึงไม่ต้องขอสิทธิ์ `sudo` สำหรับ `apt-get install espeak-ng` และ `npx playwright install-deps`
- ไม่มีชื่อ MCP server ซ้ำมาก่อน (`excalidraw`, `playwright`, `hello-lab`, `kokoro-tts` ยังไม่เคยลงทะเบียน) จึงไม่ต้อง `claude mcp remove` ตัวใด
- ไม่มี torch เดิมติดตั้งอยู่ก่อน จึงติดตั้งรุ่น CPU-only ได้ตรงตามที่กำหนด ไม่มีการดาวน์โหลด CUDA build ขนาดใหญ่

## 6. ขั้นตอนต่อไปสำหรับผู้ใช้

1. พิมพ์ `/exit` แล้วเปิด `claude` ใหม่ เพื่อให้ Claude Code โหลดค่า MCP server ที่เพิ่งลงทะเบียน (`excalidraw`, `playwright`, `hello-lab`, `kokoro-tts`) เข้าสู่ session
2. ถ้าเครื่องมีจอแสดงผล (ไม่ใช่กรณีนี้) ให้เปิด `http://127.0.0.1:3000` ในเบราว์เซอร์เพื่อใช้งาน Excalidraw ผ่าน UI ปกติ
3. เนื่องจากเครื่องนี้ไม่มีจอแสดงผล ให้ใช้ Prompt S5 เพื่อเปิด/ควบคุม Excalidraw ผ่าน Playwright MCP (`--headless`) แทนการเปิดเบราว์เซอร์โดยตรง
4. เว็บทดลอง Kokoro TTS ยังทำงานอยู่ที่ `http://127.0.0.1:8765` (pid บันทึกไว้ที่ `labs/kokoro-web/server.pid`) หยุดได้ด้วย `kill "$(cat labs/kokoro-web/server.pid)"`
