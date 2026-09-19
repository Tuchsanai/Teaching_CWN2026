# บันทึกการทดลอง: เว็บ Kokoro TTS และ MCP server ของตัวเอง

ผู้ดำเนินการ: Claude Fable 5.1 (fork ของ session yolo2) ใช้ Bash เท่านั้น · เริ่ม `start-utc.txt` · จบ `end-utc.txt` · เวอร์ชันเครื่องมือใน `run-info.json`

## ลำดับที่ทำ

1. **ตรวจ SDK และ Kokoro ก่อนเขียนโค้ด** — `mcp` 2.0.0 ไม่มี `mcp.server.fastmcp` แล้ว ใช้ `from mcp.server import MCPServer` และ `from mcp import Client`; `Client` รับ URL (Streamable HTTP), instance ของ server (in-memory) หรือ Transport เช่น `stdio_client(StdioServerParameters(...))`. ทดสอบเสียง af_heart, af_bella, am_adam, am_michael โหลดได้ทั้งสี่ (pack shape 510×1×256)
2. **เขียนเว็บ `labs/kokoro-web`** (`kokoro_core.py`, `app.py`, `static/index.html`, `run.sh`) แล้วเริ่มด้วย `./run.sh` → pid ใน `server.pid`, http://127.0.0.1:8765, `KOKORO_DEVICE=cpu`
3. **ตรวจเว็บด้วย curl** — `web-curl-health.json` (ก่อนโหลดโมเดล `model_loaded: false`), `web-curl-tts.json` + `web-curl-tts-time.txt` (ครั้งแรกรวมโหลดโมเดล 6.66 s; `gen_ms` 672; เสียงยาว 3.98 s), `web-curl-tts-second.txt` (ครั้งที่สอง 0.55 s), `web-wav-check.txt` (24000 Hz, mono, PCM_16, ไม่เงียบ), `web-curl-tts-empty.txt` (ข้อความว่าง → HTTP 400 `text must not be empty`)
4. **เขียน `labs/my-mcp-server`** — `hello_server.py`, `tts_server.py`, `wire_capture.py`, `client_test.py`, `mcp.json`, `codex-config-snippet.toml`, `claude_lab.sh`, `summarize_stream.py`, `README-run.md`
5. **Python client ↔ hello_server ผ่าน stdio + wire_capture** → `client-hello-output.txt`, `wire-hello.jsonl` (18 บรรทัด) — client ของ SDK 2.0 เปิดด้วย `server/discover` และแนบ `_meta.io.modelcontextprotocol/protocolVersion = "2026-07-28"` ทุกคำขอ ไม่มี `initialize`; add(17,25) → 42; count_words → 9 คำ 56 ตัวอักษร
6. **Python client ↔ tts_server** → `client-tts-output.txt`, `wire-tts.jsonl`, `speak-output.wav` (4.45 s, gen 693 ms, cpu)
7. **Streamable HTTP** — รัน `hello_server.py --http` (127.0.0.1:8766/mcp) แล้ว `client_test.py --server http` ผ่านครบ (`client-http-output.txt`) และทดลอง curl ดิบ 5 รอบใน `http-curl.txt`:
   - รอบ 1–3: ไม่ใส่ header พิเศษ → `400 Bad Request: Missing session ID`; ใส่ `mcp-session-id` ที่ server แจกมา → ได้ `-32601 Method not found: server/discover` และ `-32602 Invalid request parameters` (server เข้าโหมด session แบบเก่า)
   - รอบ 4: ใส่ `MCP-Protocol-Version: 2026-07-28` → `-32020 mcp-method header does not match the request body's method`
   - รอบ 5 (สำเร็จ): ใส่ `MCP-Protocol-Version`, `Mcp-Method: <method>` และ `Mcp-Name: add` สำหรับ tools/call → 200 ทั้ง `server/discover`, `tools/list`, `tools/call` (ผล 42) ตอบเป็น JSON ตรง ๆ ไม่ต้องมี session
   - ข้อผิดพลาดระหว่างทาง: ใช้ `pkill -f 'hello_server.py --http'` แล้วไปฆ่า shell ของตัวเอง (exit 144) จึงเปลี่ยนมาเก็บ pid และ `kill <pid>` แทน
8. **Claude Code (โปรไฟล์ yolo1, `--model sonnet --effort medium`) 3 รอบต่อเนื่องด้วย `claude_lab.sh`** (`claude-*-stream.jsonl`, `claude-*-summary.md`, wire log แยกต่อรอบ):
   - `discover` (7.1 s, exit 0): system/init รายงาน `hello-lab` และ `kokoro-tts` สถานะ `connected`; host มองเห็น tool ชื่อ `mcp__hello-lab__add`, `mcp__hello-lab__count_words`, `mcp__hello-lab__get_time`, `mcp__kokoro-tts__list_voices`, `mcp__kokoro-tts__speak`; Claude ใช้ `ToolSearch` โหลด schema แล้วตอบรายชื่อพร้อมพารามิเตอร์โดยไม่เรียก tool
   - `use` (9.7 s, 6 turn): เรียก `mcp__hello-lab__add {"a":17,"b":25}` → 42, `get_time` → 2026-09-19T06:30:20Z, `count_words` → 9 คำ, และอ่าน resource ผ่าน `ReadMcpResourceTool {"server":"hello-lab","uri":"lab://info"}`
   - `tts` (13.7 s): เรียก `mcp__kokoro-tts__speak {"text": "Model Context Protocol lets one server serve many agents."}` → ไฟล์ `.wav` 4.45 s (gen 684 ms)
   - บนสาย (`claude-*-wire-*.jsonl`): Claude Code 2.1.258 ส่ง `initialize` พร้อม `protocolVersion: "2025-11-25"` และ `clientInfo {"name":"claude-code","version":"2.1.258"}` ตามด้วย `notifications/initialized`, `tools/list`, `prompts/list`, `resources/list` — server SDK 2.0 ตอบทั้งแบบเก่า (initialize) และแบบใหม่ (server/discover) ได้
9. **Codex CLI** — ไม่ได้รัน (โควตารายสัปดาห์ของบัญชี cyolo1 ใช้ไป 95% ตาม snapshot 2026-09-16) มีเพียง `codex-config-snippet.toml`
10. เขียน `run-info.json`, `sha256.json` (16 ไฟล์ใน labs/kokoro-web และ labs/my-mcp-server), `trace.md`

## สถานะตอนจบ
- เว็บ Kokoro ยังรันอยู่ที่ http://127.0.0.1:8765 (pid ใน `labs/kokoro-web/server.pid`) เพื่อให้แล็บ Playwright ใช้ต่อ
- MCP server แบบ HTTP (8766) ปิดแล้ว
- GPU: ไม่ได้ใช้ในรอบนี้ (cpu) — ถ้าจะใช้ cuda บนเครื่องนี้ต้อง `torch.backends.cudnn.enabled = False` ก่อน (ทำไว้ใน `kokoro_core.py` แล้ว)
