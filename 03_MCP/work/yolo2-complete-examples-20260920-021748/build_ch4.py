import pathlib
root = pathlib.Path("/root/workspace/CWN/Teaching/03_MCP")
p = root/"readme.md"
t = p.read_text(encoding="utf-8")

start = t.index("#### 4.6.1 สิ่งที่ต้องมีก่อน")
end = t.index("#### 4.6.8 หมายเหตุสำหรับ Windows")

new = r'''#### 4.6.1 สิ่งที่ต้องมีก่อน (ครั้งเดียวต่อเครื่อง)

```bash
node -v && npm -v        # ต้อง v18 ขึ้นไป (Excalidraw MCP 2.0 ต้องการ v20 ขึ้นไป; เครื่องเรียนใช้ v24.20.0)
python3 --version        # ต้อง 3.10 ขึ้นไป (เครื่องเรียนใช้ 3.12.3) — Ubuntu: sudo apt-get install -y python3 python3-venv python3-pip
git --version
claude --version         # ใช้ Claude Code เป็น Host (เครื่องเรียนใช้ 2.1.258)
codex --version          # ใช้ Codex CLI เป็น Host (เครื่องเรียนใช้ codex-cli 0.154.0)
```

ถ้ายังไม่มี Host ให้ติดตั้งแล้วล็อกอินก่อน (รายละเอียดในบทที่ 01)

```bash
curl -fsSL https://claude.ai/install.sh | bash     # Claude Code (Linux/macOS) แล้วเปิดเทอร์มินัลใหม่
claude                                             # เปิดครั้งแรก แล้วพิมพ์ /login
npm install -g @openai/codex                       # Codex CLI
codex login                                        # ล็อกอินด้วยบัญชี ChatGPT หรือ API key
```

#### 4.6.2 Python virtual environment, แพ็กเกจ และไลบรารี Kokoro

```bash
cd <PATH_TO_03_MCP>
python3 -m venv labs/.venv
labs/.venv/bin/pip install --upgrade pip
labs/.venv/bin/pip install "mcp[cli]" soundfile fastapi uvicorn
labs/.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu   # torch รุ่น CPU (ข้ามถ้ามี torch อยู่แล้ว) ~26 วินาทีในการทดสอบ
labs/.venv/bin/pip install kokoro                                                   # ~23 วินาที (โมเดล Kokoro-82M ดาวน์โหลดตอนใช้ครั้งแรก)
sudo apt-get update && sudo apt-get install -y espeak-ng                            # Linux (Debian/Ubuntu); macOS: brew install espeak-ng (แนวทาง — ยังไม่ได้ทดลอง)
labs/.venv/bin/pip list | grep -iE "^(mcp|kokoro|torch|fastapi|uvicorn|soundfile) "   # ตรวจเวอร์ชัน
```

**ทดสอบ Kokoro แบบไลบรารีล้วน ๆ ก่อน (ยังไม่เกี่ยวกับ MCP)** — ขั้นนี้พิสูจน์ว่า repo ต้นทางให้ "ไลบรารี" มา ไม่ใช่ MCP server

```bash
cat > /tmp/kokoro_smoke.py <<'PY'
"""ทดสอบ Kokoro แบบไลบรารีล้วน ๆ (ยังไม่เกี่ยวกับ MCP)"""
from kokoro import KPipeline
import soundfile as sf

pipeline = KPipeline(lang_code="a", device="cpu")   # 'a' = American English
for i, (graphemes, phonemes, audio) in enumerate(pipeline("Kokoro library test, no MCP yet.", voice="af_heart")):
    sf.write(f"/tmp/kokoro-lib-{i}.wav", audio, 24000)
    print("wrote", f"/tmp/kokoro-lib-{i}.wav", "frames:", len(audio))
PY
labs/.venv/bin/python /tmp/kokoro_smoke.py
```

ผลรันจริงบนเครื่องเรียนด้วย `/opt/venv/bin/python` (20 กันยายน 2026, exit code 0 — เก็บไว้ที่ [`kokoro-library-only-stdout.txt`](lab-results/documentation-check/run-2026-09-20-022330/kokoro-library-only-stdout.txt))

```text
WARNING: Defaulting repo_id to hexgrad/Kokoro-82M. Pass repo_id='hexgrad/Kokoro-82M' to suppress this warning.
wrote /tmp/kokoro-lib-0.wav frames: 81000
```

81000 เฟรมที่ 24000 Hz = 3.375 วินาที · ใช้ `device="cpu"` เสมอบนเครื่องที่ไม่มี GPU ที่ตั้งค่าไว้ ถ้าปล่อยให้เลือกเองบนเครื่องเรียน (RTX + torch nightly) จะได้ `RuntimeError: GET was unable to find an engine to execute this computation` (พบจริงในรอบตรวจนี้ และเป็นเหตุผลที่ [`kokoro_core.py`](labs/kokoro-web/kokoro_core.py) อ่าน `KOKORO_DEVICE` โดยมีค่าเริ่มต้นเป็น `cpu`) · สังเกตว่า `WARNING` ออกทาง **stdout** ซึ่งเป็นกับดักของ MCP แบบ stdio (ดูข้อ 3.1 และ 4.7)

#### 4.6.3 ติดตั้งเครื่องมือทีละตัว (ครบทุกขั้นของแต่ละตัว)

**ก. Excalidraw MCP — เป็น MCP server พร้อมใช้ ติดตั้งแล้วใช้ได้เลย**

```bash
npm install -g mcp-excalidraw-server              # ~เพิ่ม sudo ถ้า npm global ต้องใช้สิทธิ์
command -v mcp-excalidraw-server                  # ต้องพิมพ์ path ออกมา
mcp-excalidraw-server --help                      # ดูรายการคำสั่งของ CLI และค่าเริ่มต้นของ canvas
mcp-excalidraw-server start                       # เปิด canvas server แบบ detached
mcp-excalidraw-server status                      # ตรวจว่า canvas ตอบ (running, url, elements, browserClients)
# mcp-excalidraw-server stop                      # หยุด canvas เมื่อเลิกใช้
```

ตัวแปรสภาพแวดล้อมที่ใช้บ่อย (ตั้งตอนลงทะเบียน MCP หรือ export ก่อนเรียก CLI)

| ตัวแปร | ความหมาย | ค่าเริ่มต้นตาม CLI | ค่าจริงบนเครื่องเรียนของผู้สอน |
| --- | --- | --- | --- |
| `EXPRESS_SERVER_URL` | URL ของ canvas ที่ทั้ง MCP server และ CLI จะคุยด้วย | `http://127.0.0.1:3000` | `http://127.0.0.1:8892` |
| `EXCALIDRAW_NO_AUTOSTART` | `1` = ห้ามคำสั่ง CLI เปิด canvas ให้เอง (ใช้เมื่อมี canvas เปิดอยู่แล้ว) | ไม่ตั้ง (auto-start) | `1` |
| `EXCALIDRAW_EXPORT_DIR` | โฟลเดอร์เดียวที่อนุญาตให้เขียน/อ่านไฟล์ export | ไม่ตั้ง | `/root/workspace/.mcp/excalidraw/diagrams` |

ตรวจแบบไม่ผ่าน LLM (ผลจริงจากเครื่องเรียนเมื่อ 20 กันยายน 2026 — canvas ที่ผู้สอนเปิดค้างไว้)

```bash
EXCALIDRAW_NO_AUTOSTART=1 EXPRESS_SERVER_URL=http://127.0.0.1:8892 mcp-excalidraw-server status
```

```json
{
  "running": true,
  "url": "http://127.0.0.1:8892",
  "pid": 816,
  "elements": 21,
  "browserClients": 1,
  "success": true,
  "elementCount": 21,
  "websocketClients": 1
}
```

`browserClients` ต้องมากกว่า 0 ก่อนสั่ง `screenshot`/`export` — นั่นคือต้องมีแท็บเบราว์เซอร์เปิดหน้า canvas อยู่ ถ้าเครื่องไม่มีจอ ให้ Playwright MCP เปิดแท็บให้ (S5 ข้อ 2)

**ข. Playwright MCP — เป็น MCP server พร้อมใช้ แต่ต้องดาวน์โหลดเบราว์เซอร์เพิ่ม**

```bash
npm install -g @playwright/mcp                    # เครื่องเรียนใช้ 0.0.80
command -v playwright-mcp
npx playwright install chromium                   # ดาวน์โหลดเบราว์เซอร์ (~30 วินาที)
sudo npx playwright install-deps chromium         # Linux เท่านั้น: ไลบรารีระบบที่ Chromium ต้องใช้ (~15 วินาที)
playwright-mcp --help | head -40                  # **ตรวจชื่อตัวเลือกของเวอร์ชันที่ติดตั้งจริงก่อนใช้**
```

ตัวเลือกที่ต้องรู้ (ยืนยันจาก `playwright-mcp --help` ของ 0.0.80 บนเครื่องเรียน)

| ตัวเลือก | ใช้เมื่อไร |
| --- | --- |
| `--browser <browser>` | เลือกเบราว์เซอร์ help ของ 0.0.80 ระบุค่าที่รับได้ว่า `chrome, firefox, webkit, msedge` ส่วนการทดลองในคอนเทนเนอร์เมื่อ 19 กันยายน 2026 ใช้ `@playwright/mcp` 0.0.82 กับค่า `chromium` แล้วผ่าน — **ให้ยึด help ของเวอร์ชันที่ติดตั้งจริง** ถ้าค่าถูกปฏิเสธให้เปลี่ยนไปใช้ค่าที่ help ระบุ |
| `--headless` | เครื่องไม่มีจอ (server / WSL ไม่มี GUI / container) |
| `--no-sandbox` | รันเป็น root (container) ไม่ใส่จะได้ `Running as root without --no-sandbox is not supported` |
| `--cdp-endpoint <url>` | ต่อกับเบราว์เซอร์ที่เปิดค้างไว้แล้วแทนการเปิดใหม่ — เครื่องเรียนใช้ `http://127.0.0.1:9222` |
| `--output-dir <path>` | โฟลเดอร์เก็บ screenshot/ไฟล์ที่ tool สร้าง |
| `--isolated` | ไม่เก็บโปรไฟล์เบราว์เซอร์ลงดิสก์ |

**ค. Kokoro TTS — ไม่ใช่ MCP server ต้องมีคนห่อ**

repo ต้นทาง <https://github.com/hexgrad/kokoro> ให้ **ไลบรารี Python** มาอย่างเดียว (ติดตั้งแล้วในข้อ 4.6.2) ไม่มีคำสั่งอย่าง `kokoro-mcp-server` ให้รัน สิ่งที่ทำให้ Kokoro กลายเป็น MCP tool คือ wrapper ที่เราเขียนเอง — ในบทเรียนนี้คือ [`labs/my-mcp-server/tts_server.py`](labs/my-mcp-server/tts_server.py) (20 บรรทัดแรกของบทที่ 7 สอนวิธีเขียน) ดังนั้นลำดับที่ถูกต้องคือ

```bash
labs/.venv/bin/pip show kokoro | head -3                                   # 1. มีไลบรารีแล้ว
labs/.venv/bin/python /tmp/kokoro_smoke.py                                 # 2. ไลบรารีสร้างเสียงได้จริง
labs/.venv/bin/python labs/my-mcp-server/direct_call_kokoro.py --skip-sanity   # 3. wrapper ทำงานผ่าน MCP ได้จริง (ยังไม่ต้องมี Host)
```

**สรุปว่าอะไรติดตั้งได้เลย อะไรต้องเขียน wrapper**

| เครื่องมือ | ต้นทางให้อะไรมา | คำสั่งติดตั้ง | ต้องเขียน MCP server เองไหม |
| --- | --- | --- | --- |
| Excalidraw MCP | MCP server + CLI พร้อมใช้ | `npm install -g mcp-excalidraw-server` | ไม่ต้อง |
| Playwright MCP | MCP server พร้อมใช้ | `npm install -g @playwright/mcp` + `npx playwright install chromium` | ไม่ต้อง |
| Kokoro TTS | ไลบรารี Python (โมเดล Kokoro-82M) | `pip install kokoro` (+ `espeak-ng`) | **ต้อง** — ในบทเรียนใช้ `labs/my-mcp-server/tts_server.py` |
| hello-lab | ไม่มีต้นทาง เป็นแล็บของบทเรียน | `pip install "mcp[cli]"` | **ต้อง** — `labs/my-mcp-server/hello_server.py` (บทที่ 7) |

**พอร์ตและ path ที่บทเรียนนี้ใช้**

| บริการ | พอร์ต/path | ใครเปิด | ตรวจด้วย |
| --- | --- | --- | --- |
| Excalidraw canvas | `http://127.0.0.1:3000` (ค่าเริ่มต้นของ CLI) หรือ `http://127.0.0.1:8892` (เครื่องเรียน ตั้งผ่าน `EXPRESS_SERVER_URL`) | `mcp-excalidraw-server start` | `mcp-excalidraw-server status` |
| เว็บทดลอง Kokoro (FastAPI) | `http://127.0.0.1:8765` | `labs/kokoro-web/run.sh` | `curl -s http://127.0.0.1:8765/api/health` |
| `hello_server.py` แบบ Streamable HTTP | `http://127.0.0.1:8766/mcp` | `hello_server.py --http` | `client_test.py --server http` |
| headless Chrome ของเครื่องเรียน (CDP) | `http://127.0.0.1:9222` | เปิดไว้ล่วงหน้าโดยผู้สอน | `curl -s http://127.0.0.1:9222/json/version` |
| ไฟล์เสียงที่สร้าง | `labs/kokoro-web/audio_out/*.wav` | `kokoro_core.synthesize()` | `ls -lt labs/kokoro-web/audio_out \| head` |

#### 4.6.4 ลงทะเบียน MCP server กับ Claude Code

```bash
cd <PATH_TO_03_MCP>

# 1) Excalidraw — แบบพื้นฐาน (canvas ใช้ค่าเริ่มต้น http://127.0.0.1:3000)
claude mcp add --scope user excalidraw -- mcp-excalidraw-server

# 1b) Excalidraw — แบบเดียวกับเครื่องเรียน (canvas อยู่พอร์ต 8892 และเปิดค้างไว้แล้ว)
# claude mcp add --scope user excalidraw \
#   -e EXPRESS_SERVER_URL=http://127.0.0.1:8892 \
#   -e EXCALIDRAW_NO_AUTOSTART=1 \
#   -e EXCALIDRAW_EXPORT_DIR=/root/workspace/.mcp/excalidraw/diagrams \
#   -- mcp-excalidraw-server

# 2) Playwright — เลือกบรรทัดเดียวให้ตรงกับเครื่อง (ตรวจชื่อค่าของ --browser จาก playwright-mcp --help ก่อน)
claude mcp add --scope user playwright -- playwright-mcp --browser chrome                              # เครื่องที่มีจอ
# claude mcp add --scope user playwright -- playwright-mcp --browser chrome --headless                 # เครื่องไม่มีจอ
# claude mcp add --scope user playwright -- playwright-mcp --browser chrome --headless --no-sandbox    # รันเป็น root ใน container
# claude mcp add --scope user playwright -- playwright-mcp --cdp-endpoint http://127.0.0.1:9222        # ต่อเบราว์เซอร์ที่เปิดค้างไว้ (แบบเครื่องเรียน)

# 3) แล็บของบทเรียน (ต้องมีโฟลเดอร์ labs/ ก่อน)
claude mcp add --scope user hello-lab  -- "$(pwd)/labs/.venv/bin/python" "$(pwd)/labs/my-mcp-server/hello_server.py"
claude mcp add --scope user kokoro-tts -e KOKORO_DEVICE=cpu -- "$(pwd)/labs/.venv/bin/python" "$(pwd)/labs/my-mcp-server/tts_server.py"

# 4) ตรวจผล
claude mcp list                 # ต้องเห็น ✔ Connected ครบทุกตัว
claude mcp get playwright       # ดูค่าที่ลงทะเบียนของตัวใดตัวหนึ่ง
# claude mcp remove playwright  # ถอนก่อนลงทะเบียนใหม่ (ชื่อซ้ำจะ error)
```

ตัวเลือก `--scope`: `user` = ใช้ได้ทุกโฟลเดอร์ (เก็บใน `~/.claude.json`), `project` = เก็บใน `.mcp.json` ของโฟลเดอร์ปัจจุบันเพื่อแชร์ผ่าน git (Claude Code จะถามอนุมัติครั้งแรกที่เปิด), `local` (ค่าเริ่มต้น) = เฉพาะโฟลเดอร์นี้บนเครื่องนี้ · ตัวเลือกกำหนดตัวแปรสภาพแวดล้อมคือ `-e KEY=value` (ใส่ซ้ำได้หลายตัว) · หลังลงทะเบียนต้อง `/exit` แล้วเปิด `claude` ใหม่ Host จึงจะโหลด server

#### 4.6.5 เริ่มเว็บทดลองและทดสอบโดยไม่ใช้ LLM

```bash
cd <PATH_TO_03_MCP>
PYTHON="$(pwd)/labs/.venv/bin/python" labs/kokoro-web/run.sh                     # เปิด http://127.0.0.1:8765 (pid ใน labs/kokoro-web/server.pid)
curl -s http://127.0.0.1:8765/api/health                                         # {"ok":true,"device":"cpu",...}
curl -s -X POST http://127.0.0.1:8765/api/tts -H "Content-Type: application/json" \
     -d '{"text":"Setup test from prompt.","voice":"af_heart"}'                  # ครั้งแรก ~3 วินาที (โหลดโมเดล) ครั้งต่อไปต่ำกว่า 1 วินาที
labs/.venv/bin/python labs/my-mcp-server/client_test.py --server hello           # ต้องเห็น tools/list และ add(17, 25) → 42
labs/.venv/bin/python labs/my-mcp-server/direct_call_kokoro.py                   # เรียก MCP tool ตรง ๆ ครบวงจร (ดูข้อ 3.1) exit code 0 = ผ่าน
kill "$(cat labs/kokoro-web/server.pid)"                                         # หยุดเว็บเมื่อเลิกใช้
```

ผลจริงของ `curl /api/health` บนเครื่องเรียนเมื่อ 20 กันยายน 2026: `{"ok":true,"device":"cpu","model_loaded":true,"voices":["af_heart","af_bella","am_adam","am_michael"]}`

#### 4.6.6 ไฟล์ตั้งค่าที่คำสั่งด้านบนสร้างให้ (แก้เองได้)

ระดับผู้ใช้ `~/.claude.json` ส่วน `mcpServers` ตามรูปแบบที่การติดตั้งสร้างให้ (ค่าจริงหลังรันพรอมป์ต์ติดตั้งฉบับละเอียดในข้อ 4.6.9 เมื่อการทดสอบ 19 กันยายน 2026อยู่ใน [`container-state-after-s0.txt`](lab-results/setup-prompt/run-2026-09-19-072524/container-state-after-s0.txt) ซึ่งตอนนั้น `playwright` มี `args` เพียง `["--headless"]` ก่อนที่พรอมป์ต์จะถูกปรับให้ใส่ `--browser`; แทน path ด้วยตัวยึด `<PATH_TO_03_MCP>`)

```json
{
  "mcpServers": {
    "excalidraw": {"type": "stdio", "command": "mcp-excalidraw-server", "args": [], "env": {}},
    "playwright": {"type": "stdio", "command": "playwright-mcp", "args": ["--browser", "chrome", "--headless"], "env": {}},
    "hello-lab":  {"type": "stdio", "command": "<PATH_TO_03_MCP>/labs/.venv/bin/python",
                   "args": ["<PATH_TO_03_MCP>/labs/my-mcp-server/hello_server.py"], "env": {}},
    "kokoro-tts": {"type": "stdio", "command": "<PATH_TO_03_MCP>/labs/.venv/bin/python",
                   "args": ["<PATH_TO_03_MCP>/labs/my-mcp-server/tts_server.py"], "env": {"KOKORO_DEVICE": "cpu"}}
  }
}
```

ค่าจริงบนเครื่องเรียนของผู้สอน (คัดเฉพาะสอง server แรกจากไฟล์ตั้งค่าของ Host ที่ใช้สอน — ต่อเบราว์เซอร์ที่เปิดค้างไว้ และ canvas อยู่พอร์ต 8892)

```json
{
  "mcpServers": {
    "playwright": {"type": "stdio", "command": "playwright-mcp",
                   "args": ["--cdp-endpoint", "http://127.0.0.1:9222",
                            "--output-dir", "/root/workspace/.mcp/playwright/output"]},
    "excalidraw": {"type": "stdio", "command": "mcp-excalidraw-server", "args": [],
                   "env": {"EXPRESS_SERVER_URL": "http://127.0.0.1:8892",
                           "EXCALIDRAW_EXPORT_DIR": "/root/workspace/.mcp/excalidraw/diagrams",
                           "EXCALIDRAW_NO_AUTOSTART": "1"}}
  }
}
```

ระดับโปรเจกต์ `.mcp.json` (วางไว้ในโฟลเดอร์ `03_MCP` แล้ว commit ได้ รูปแบบเดียวกัน)

```json
{
  "mcpServers": {
    "excalidraw": {"command": "mcp-excalidraw-server", "args": []},
    "playwright": {"command": "playwright-mcp", "args": ["--browser", "chrome"]},
    "hello-lab":  {"command": "<PATH_TO_03_MCP>/labs/.venv/bin/python", "args": ["<PATH_TO_03_MCP>/labs/my-mcp-server/hello_server.py"]},
    "kokoro-tts": {"command": "<PATH_TO_03_MCP>/labs/.venv/bin/python", "args": ["<PATH_TO_03_MCP>/labs/my-mcp-server/tts_server.py"], "env": {"KOKORO_DEVICE": "cpu"}}
  }
}
```

ชั่วคราวเฉพาะคำสั่งเดียว (ไม่แตะการตั้งค่าเครื่อง ใช้เก็บหลักฐานในบทที่ 7): `claude -p --strict-mcp-config --mcp-config labs/my-mcp-server/mcp.json "<prompt>"` — ไฟล์ [`labs/my-mcp-server/mcp.json`](labs/my-mcp-server/mcp.json) เป็นตัวอย่างที่ห่อ server ด้วย `wire_capture.py` เพื่อดักข้อความบนสาย (ไฟล์จริงใช้ path เต็ม ที่นี่ย่อให้อ่านง่าย)

```json
{
  "mcpServers": {
    "hello-lab": {
      "command": "/opt/venv/bin/python",
      "args": ["<PATH_TO_03_MCP>/labs/my-mcp-server/wire_capture.py", "--log", "<PATH_TO_03_MCP>/labs/my-mcp-server/wire-claude-hello.jsonl",
               "--", "/opt/venv/bin/python", "<PATH_TO_03_MCP>/labs/my-mcp-server/hello_server.py"]
    },
    "kokoro-tts": {
      "command": "/opt/venv/bin/python",
      "args": ["<PATH_TO_03_MCP>/labs/my-mcp-server/wire_capture.py", "--log", "<PATH_TO_03_MCP>/labs/my-mcp-server/wire-claude-tts.jsonl",
               "--", "/opt/venv/bin/python", "<PATH_TO_03_MCP>/labs/my-mcp-server/tts_server.py"],
      "env": {"KOKORO_DEVICE": "cpu"}
    }
  }
}
```

เมื่อต่อสำเร็จ Claude Code จะมองเห็น tool ในชื่อ `mcp__<ชื่อ server>__<ชื่อ tool>` เช่น `mcp__hello-lab__add` และ `mcp__kokoro-tts__speak` (ดู [`claude-discover-summary.md`](lab-results/own-server/run-2026-09-19-062712/claude-discover-summary.md)) ส่วน resource อ่านผ่านเครื่องมือกลาง `ReadMcpResourceTool {"server": "hello-lab", "uri": "lab://info"}`

#### 4.6.7 Codex CLI — คำสั่งติดตั้งและตั้งค่าครบทุกเครื่องมือ

ขั้นตอนก่อนหน้า (4.6.1–4.6.3) ใช้ร่วมกันทั้งสอง Host เพราะเป็นการติดตั้งแพ็กเกจ ต่างกันเฉพาะขั้นลงทะเบียน รันจากโฟลเดอร์ `03_MCP` บน Linux/macOS

```bash
cd <PATH_TO_03_MCP>

# 1) Excalidraw
codex mcp add excalidraw -- "$(command -v mcp-excalidraw-server)"
# แบบเดียวกับเครื่องเรียน (canvas พอร์ต 8892 เปิดค้างไว้แล้ว):
# codex mcp add excalidraw \
#   --env EXPRESS_SERVER_URL=http://127.0.0.1:8892 \
#   --env EXCALIDRAW_NO_AUTOSTART=1 \
#   --env EXCALIDRAW_EXPORT_DIR=/root/workspace/.mcp/excalidraw/diagrams \
#   -- "$(command -v mcp-excalidraw-server)"

# 2) Playwright (ตรวจค่าที่ --browser รับได้จาก playwright-mcp --help ของเวอร์ชันที่ติดตั้ง)
codex mcp add playwright -- "$(command -v playwright-mcp)" --browser chrome
# เครื่องไม่มีจอ: เติม --headless ต่อท้าย · รันเป็น root ใน container: เติม --headless --no-sandbox
# ต่อเบราว์เซอร์ที่เปิดค้างไว้: codex mcp add playwright -- "$(command -v playwright-mcp)" --cdp-endpoint http://127.0.0.1:9222

# 3) แล็บของบทเรียน
codex mcp add hello-lab  -- "$(pwd)/labs/.venv/bin/python" "$(pwd)/labs/my-mcp-server/hello_server.py"
codex mcp add kokoro-tts --env KOKORO_DEVICE=cpu -- "$(pwd)/labs/.venv/bin/python" "$(pwd)/labs/my-mcp-server/tts_server.py"

# 4) ตรวจค่าที่ลงทะเบียน
codex mcp list
codex mcp get playwright
# codex mcp remove playwright   # ถอนทีละตัวเมื่อต้องแก้
```

รูปแบบคำสั่ง (`--env KEY=VALUE`, `-- <COMMAND>...`, `--url` สำหรับ Streamable HTTP) ยืนยันจาก `codex mcp add --help` ของ `codex-cli` 0.154.0 บนเครื่องเรียนเมื่อ 20 กันยายน 2026 · เปิด `codex` เป็น session ใหม่ ใช้ `/mcp` ดู server ที่ใช้งานอยู่ แล้วใช้ S5 ทดสอบจริง — `codex mcp list` แสดงค่าที่ลงทะเบียน **ไม่ใช่** หลักฐานว่าทุก tool ทำงานผ่านแล้ว · เอกสารอ้างอิง: [MCP ของ OpenAI](https://developers.openai.com/codex/mcp) · **ยังไม่ได้ทดสอบติดตั้งครบชุดด้วย Codex ในรอบนี้** (รอบนี้ตรวจเฉพาะ `codex mcp add --help` แบบอ่านอย่างเดียว)

Codex เก็บค่าไว้ใน `~/.codex/config.toml` (หรือ `$CODEX_HOME/config.toml`) ถ้าจะแก้เองให้วางส่วนนี้ต่อท้ายไฟล์แล้วตรวจด้วย `codex mcp list`

```toml
[mcp_servers.excalidraw]
command = "mcp-excalidraw-server"

[mcp_servers.excalidraw.env]
EXPRESS_SERVER_URL = "http://127.0.0.1:8892"
EXCALIDRAW_NO_AUTOSTART = "1"
EXCALIDRAW_EXPORT_DIR = "/root/workspace/.mcp/excalidraw/diagrams"

[mcp_servers.playwright]
command = "playwright-mcp"
args = ["--browser", "chrome"]
# เครื่องเรียนของผู้สอนใช้: args = ["--cdp-endpoint", "http://127.0.0.1:9222"]

[mcp_servers.hello-lab]
command = "<PATH_TO_03_MCP>/labs/.venv/bin/python"
args = ["<PATH_TO_03_MCP>/labs/my-mcp-server/hello_server.py"]

[mcp_servers.kokoro-tts]
command = "<PATH_TO_03_MCP>/labs/.venv/bin/python"
args = ["<PATH_TO_03_MCP>/labs/my-mcp-server/tts_server.py"]

[mcp_servers.kokoro-tts.env]
KOKORO_DEVICE = "cpu"
```

เมื่อต้องถอน ใช้ `codex mcp remove <ชื่อ server>` ทีละตัว ได้แก่ `excalidraw`, `playwright`, `hello-lab`, `kokoro-tts` ส่วนการหยุดเว็บ Kokoro และ canvas ใช้ขั้นตอนเดียวกับ S6 · ถ้าใช้ Codex เป็น Host ให้เริ่มจากคำขอภาษาธรรมดาในข้อ 4.2.2 ก่อน แล้วใช้คำสั่งด้านบนเป็นตัวเทียบผลเท่านั้น

'''

t = t[:start] + new + t[end:]
p.write_text(t, encoding="utf-8")
print("4.6 rewritten:", len(new), "chars")
