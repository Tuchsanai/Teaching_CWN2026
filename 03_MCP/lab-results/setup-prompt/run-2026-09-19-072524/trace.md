# บันทึกการทดสอบ Setup Prompt ในคอนเทนเนอร์เปล่า

ผู้ดำเนินการ: Claude Fable 5.1 (fork ของ session yolo2) ใช้ Bash เท่านั้น · คอนเทนเนอร์ `devtools-mcpsetup-4d8027` (image tuchsanai/devtools:2569_1, --privileged, ไม่ map port ใช้ docker exec) · เริ่ม 2026-09-19T07:25:24Z · จบ 2026-09-19T07:43:30Z

## ลำดับที่ทำ

1. **เตรียมคอนเทนเนอร์** — `docker run -dit --name devtools-mcpsetup-4d8027 --privileged tuchsanai/devtools:2569_1`; คัดลอก `03_MCP/labs` (ลบ .venv, audio_out, __pycache__, wire-*.jsonl ออกก่อน) ไปที่ `/root/03_MCP/labs`; ติดตั้ง Claude Code ด้วย `curl -fsSL https://claude.ai/install.sh | bash` → **2.1.278**; คัดลอก credential ของบัญชีทดสอบ (mode 600) และเขียน `~/.claude.json` ให้ข้าม onboarding; `claude auth status` → loggedIn true
2. **S0 ครั้งที่ 0 (ล้มเหลวทันที)** — `claude --dangerously-skip-permissions -p ...` ในคอนเทนเนอร์ที่เป็น root ได้ stderr: `--dangerously-skip-permissions cannot be used with root/sudo privileges for security reasons` (ไฟล์ `s0-attempt0-stderr.txt`) → เพิ่ม `export IS_SANDBOX=1` ในสคริปต์รัน (ไม่ได้แก้ prompt)
3. **S0 ครั้งที่ 1 (สำเร็จ)** — 07:27:43Z → 07:32:07Z (4 นาที 24 วินาที) exit 0, 38 turn; Claude ทำครบทั้ง 9 ข้อของ prompt: venv, pip (mcp 2.2.0, torch CPU, kokoro), apt espeak-ng, npm -g 2 แพ็กเกจ, playwright install chromium + install-deps, `claude mcp add --scope user` 4 ตัว (เลือกใส่ `--headless` ให้ playwright เองเพราะตรวจพบว่าไม่มีจอ), run.sh เว็บ Kokoro, curl health + POST /api/tts, client_test.py → 42, `claude mcp list` Connected ทั้ง 4, เขียน `labs/setup-report.md` (ดู `s0-summary.md`, `s0-stream.jsonl`, `setup-report.md`, `container-state-after-s0.txt`) · ข้อผิดพลาดเดียวระหว่างทาง: tool call `sleep 60; echo done` ถูก Claude Code บล็อก Claude เปลี่ยนไป poll แทน
4. **S5 รอบที่ 1 (3/5)** — session ใหม่ 07:34:11Z, 4 นาที 9 วินาที; `add` = 42 และ `speak` ผ่าน; Playwright MCP ล้มเหลว 2 ชั้น: (ก) `Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome Run "npx playwright install chrome"` → Claude ติดตั้ง chrome (ข) `Chromium sandboxing failed! ... Running as root without --no-sandbox is not supported. See https://crbug.com/638180.` → Claude แก้ `~/.claude.json` ให้ playwright ใช้ `--headless --no-sandbox` แต่ค่าใหม่ยังไม่มีผลใน session เดิม; ข้อ Excalidraw ผ่านโดย Claude เปิด headless Chrome ค้างไว้เองที่ :3000 (`round1-s5-excalidraw-export.png`)
5. **S5 รอบที่ 2 (5/5)** — session ใหม่ 07:40:40Z, 52 วินาที, ไม่แก้อะไรด้วยมือ; Playwright MCP เปิด :3000 และ :8765 ได้ กรอก/คลิก/รอ "สร้างเสียงสำเร็จ" ผ่าน (เสียง 1.98 s) Excalidraw export ผ่าน (`round2-s5-excalidraw-export.png`) speak ผ่าน (2.02 s); error ที่แก้เองได้: ใช้ `target` เป็นชื่อ role แทน ref → `Unexpected token "" while parsing css selector ""`
6. **เก็บหลักฐานและลบคอนเทนเนอร์** — คัดลอก stream/summary/PNG/WAV/snapshot มาที่โฟลเดอร์นี้ แล้ว `docker rm -f devtools-mcpsetup-4d8027` (ผลอยู่ท้ายไฟล์)

## ข้อค้นพบสำหรับปรับ Setup Prompt S0/S2
- ต้องสั่ง `npx playwright install chrome` (หรือลงทะเบียน playwright ด้วย `--browser chromium`) เพราะ `@playwright/mcp` 0.0.82 ค่าเริ่มต้นใช้ Google Chrome
- เมื่อรันเป็น root (คอนเทนเนอร์/เซิร์ฟเวอร์) ต้องลงทะเบียน playwright ด้วย `--headless --no-sandbox`
- บนเครื่องไม่มีจอ Prompt S5 ต้องเปิด canvas Excalidraw ผ่าน Playwright MCP ก่อนวาด (ทำได้จริงในรอบที่ 2)
- `claude -p --dangerously-skip-permissions` ใช้กับ root ไม่ได้ถ้าไม่ตั้ง `IS_SANDBOX=1`; นักศึกษาที่ใช้ `claude` แบบ interactive ไม่เจอเพราะกดอนุมัติเอง

## Cleanup

`docker rm -f devtools-mcpsetup-4d8027` เสร็จ 2026-09-19T07:43:34Z · `docker ps -a --filter name=^devtools-mcpsetup` → ไม่มี container ค้าง
