# Design Spec — บทเรียน 03_MCP (Model Context Protocol)

วันที่ออกแบบ: 2026-09-19 · ผู้ออกแบบ: Claude Fable 5.1 (yolo2) · สถานะ: ใช้กำกับการสร้างสื่อและหลักฐานทั้งหมดในโฟลเดอร์นี้

## 1. เป้าหมายการเรียนรู้ (ต้องตอบได้หลังจบบท)
1. MCP คืออะไร และแก้ปัญหาอะไร (N×M integration → N+M ผ่านโปรโตคอลกลาง)
2. ทำไม LLM/AI Agent ต้องใช้ MCP (LLM สร้างข้อความได้ แต่ทำงานกับโลกภายนอกไม่ได้เอง; tool calling แบบเฉพาะกิจไม่ reuse ข้ามโปรแกรม)
3. โครงสร้าง Host / LLM / MCP Client / MCP Server / Tools-Resources-Prompts และลำดับข้อความ tools/list → tools/call (JSON-RPC 2.0)
4. MCP ต่างจาก Python function และ REST API ตรงไหน (discovery + schema + protocol กลาง + host เป็นผู้คุมสิทธิ์)
5. ติดตั้ง/ตั้งค่า MCP server ใน Claude Code และ Codex, ทดลองใช้ Excalidraw MCP และ Playwright MCP, และเขียน MCP server ของตัวเองด้วย Python SDK (`mcp` 2.0.0)

## 2. โครงสร้างโฟลเดอร์
```
03_MCP/
  readme.md                      สื่อการสอนไฟล์เดียว (ภาษาไทย)
  img/                           แผนภาพทุกรูปสร้างด้วย Excalidraw MCP (png + .excalidraw ต้นฉบับ)
  labs/design-spec.md            ไฟล์นี้
  labs/prompts/                  Prompt พร้อมคัดลอกสำหรับแต่ละแล็บ
  labs/kokoro-web/               เว็บทดลอง Kokoro TTS (FastAPI + หน้าเว็บเดียว) สำหรับ Case Study 2
  labs/my-mcp-server/            MCP server ที่นักศึกษาสร้างเอง + client ทดสอบ + ตัวดักข้อความ JSON-RPC
  lab-results/excalidraw/run-*/  หลักฐาน Case Study 1 (ลำดับ tool ที่ AI เรียก, ภาพก่อน/หลังแก้)
  lab-results/playwright/run-*/  หลักฐาน Case Study 2 (snapshot, screenshot, network, console)
  lab-results/own-server/run-*/  หลักฐานการทดสอบ MCP server ของตัวเอง (wire log, ผลจาก client และจาก Claude Code)
```

## 3. โครงบทเรียน readme.md
0. ภาพรวม สิ่งที่ต้องเตรียม และสิ่งที่ต้องส่ง
1. บทที่ 1 MCP คืออะไร แก้ปัญหาอะไร ทำไม Agent ต้องใช้ (d01)
2. บทที่ 2 โครงสร้าง Host/Client/Server/Tools-Resources-Prompts + ลำดับข้อความ + transport (d02, d03)
3. บทที่ 3 MCP vs Python function vs REST API (d04 + โค้ดสามแบบของงานเดียวกัน: Kokoro TTS)
4. บทที่ 4 ติดตั้งและตรวจ MCP server ใน Claude Code / Codex (config จริงของเครื่องนี้)
5. บทที่ 5 Case Study 1 Excalidraw MCP — Lab 5.1–5.4 (วาด architecture, วาด workflow, วาด flow Agent→Client→Server→Tool, แก้ diagram ด้วย prompt) (d05 + หลักฐาน)
6. บทที่ 6 Case Study 2 Playwright MCP + Kokoro web — Lab 6.1–6.7 (เปิดเว็บ, ตรวจ element, กรอกฟอร์ม, กดปุ่ม, ตรวจผล, screenshot, ใช้เป็นหลักฐาน) (d06 + หลักฐาน)
7. บทที่ 7 สร้าง MCP server ของตัวเอง — 7.1 hello server, 7.2 ทดสอบด้วย Python client + ดูข้อความจริงบนสาย, 7.3 ต่อกับ Claude Code, 7.4 kokoro-tts server (d07 + หลักฐาน)
8. บทที่ 8 สรุป แบบฝึกหัด เกณฑ์ตรวจงานส่ง อภิธานศัพท์ (d08)

## 4. แผนภาพ (ทั้งหมดวาดด้วย Excalidraw MCP โดย AI Agent จาก prompt)
| ไฟล์ | เนื้อหา |
| --- | --- |
| d01-nxm-problem | ก่อน/หลัง MCP: N×M กับ N+M |
| d02-mcp-architecture | Host (LLM + MCP Client) ↔ MCP Server ↔ Tool/Resource จริงบนเครื่องนี้ |
| d03-mcp-sequence | Prompt → Agent → Client → Server → Tool และข้อความ tools/list, tools/call, result |
| d04-three-ways | Python function vs REST API vs MCP tool |
| d05-case1-excalidraw-flow | Flow ของ Case Study 1 (ภาพก่อน/หลังแก้อยู่ใน lab-results) |
| d06-case2-playwright-flow | Prompt → AI Agent → Playwright MCP → Browser → Kokoro web → Audio |
| d07-own-server | สถาปัตยกรรม MCP server ที่สร้างเอง และวิธีทดสอบ 3 ทาง |
| d08-lesson-map | แผนที่บทเรียน |

## 5. เว็บทดลอง Kokoro (labs/kokoro-web)
- `kokoro_core.py`: ฟังก์ชัน `synthesize(text, voice) -> dict(path, duration_sec, sample_rate, gen_ms)` โหลด `KPipeline(lang_code='a')` ครั้งเดียว ใช้ GPU ถ้ามี
- `app.py`: FastAPI ที่ 127.0.0.1:8765 — `GET /` หน้าเว็บ, `POST /api/tts` (JSON {text, voice}) → {audio_url, duration_sec, sample_rate, gen_ms}, `GET /api/health`, ไฟล์เสียงเสิร์ฟจาก `/audio/<id>.wav`
- `static/index.html`: ภาษาไทย มี Text Input (`#text`), เลือกเสียง (`#voice`), ปุ่ม Speak (`#speak-btn`), Result (`#result` แสดงสถานะ, ความยาวเสียง, เวลาที่ใช้), Audio Player (`#player` `<audio controls>`), ป้ายกำกับว่า Kokoro รองรับภาษาอังกฤษ ไม่รองรับภาษาไทย
- ต้องมี `aria-label`/label ชัดเจนเพื่อให้ accessibility snapshot ของ Playwright MCP อ่านง่าย และไม่มี console error
- `run.sh` สำหรับเริ่มเซิร์ฟเวอร์ และ `requirements.txt`

## 6. MCP server ของนักศึกษา (labs/my-mcp-server)
- `hello_server.py`: `MCPServer("hello-lab")` tools `add(a:int,b:int)`, `get_time()`, `count_words(text)`; resource `lab://info`; prompt `explain_mcp(topic)`; `mcp.run()` (stdio)
- `tts_server.py`: `MCPServer("kokoro-tts")` tool `speak(text, voice="af_heart")` เรียก `kokoro_core.synthesize` แล้วคืน path + duration; tool `list_voices()`
- `wire_capture.py`: proxy stdio ที่ส่งต่อทุกบรรทัดระหว่าง client กับ server และบันทึกลง jsonl (direction, ts, message) ใช้ดูข้อความ JSON-RPC จริง
- `client_test.py`: ใช้ `mcp.Client` เชื่อม stdio subprocess → list_tools → call_tool add / speak → พิมพ์ผล
- `mcp.json` (Claude Code `--mcp-config`) และ `codex-config-snippet.toml` (Codex `[mcp_servers.*]`)
- หลักฐาน: wire log จาก Python client, wire log + output จาก `claude -p --mcp-config` (บัญชี yolo1) ที่สั่งด้วย prompt ของนักศึกษา

## 7. กติกาหลักฐาน
- ทุกตัวเลข/ข้อความ error ใน readme ต้องมาจากไฟล์ใน lab-results หรือ labs
- แนวคิดที่ไม่ได้ทดลองต้องติดป้าย "แนวทาง — ยังไม่ได้ทดลอง"
- ทุก run เก็บ `run-info.json` (วันเวลา UTC, เวอร์ชันเครื่องมือ, บัญชี/โมเดลที่ใช้) และ `trace.md`

## 8. ปรับปรุงรอบ 2 (2026-09-19 บ่าย): ติดตั้งด้วยพรอมป์ต์
ผู้ใช้ขอให้ลดขั้นตอนตั้งค่าด้วยตัวเองให้มากที่สุด จึงเปลี่ยนบทที่ 4 และทุกจุดที่มีคำสั่งติดตั้งเป็น "พรอมป์ต์ที่คัดลอกไปวางใน Claude Code ได้เลย"
- `labs/prompts/setup-00-all-in-one.md` (S0 ครบชุด), `setup-01..04` (แยกส่วน: Excalidraw, Playwright, เว็บ Kokoro, server ของนักศึกษา), `setup-05-verify.md` (ตรวจใน session ใหม่ รวมเคล็ดลับให้ Playwright เปิดแท็บ canvas ของ Excalidraw), `setup-06-remove.md`
- หลักการ: Host มี Bash → ให้ AI สร้าง venv, ติดตั้งแพ็กเกจ (torch CPU), `npm i -g`, `claude mcp add --scope user` 4 ตัว, เริ่มเว็บ, ตรวจ `claude mcp list`, เขียน `labs/setup-report.md`; นักศึกษาทำเองแค่ เปิด claude → วาง → /exit แล้วเปิดใหม่
- `labs/kokoro-web/run.sh` ใช้ `PYTHON` env (ค่าเริ่มต้น python3) แทน path ตายตัว; `README-run.md` ใช้ `python` ของ venv
- หลักฐาน: รัน S0 และ S5 ในคอนเทนเนอร์เปล่า `tuchsanai/devtools:2569_1` (ไม่มี claude/torch/chromium มาก่อน) เก็บใน `lab-results/setup-prompt/run-*/`
- รอบ 3 (ผู้ใช้ขอให้บทที่ 4 มีคำสั่งครบ ไม่ใช่แค่ชื่อไฟล์): บทที่ 4 สร้างจาก template โดยดึงข้อความพรอมป์ต์ S0–S6 จากไฟล์ใน `labs/prompts/` โดยตรง (4.2–4.4) และเพิ่มข้อ 4.6 คำสั่งติดตั้ง/ตั้งค่าแบบทำเองครบทุกขั้น (คัดจาก `setup-report.md` ที่ AI เขียนหลังติดตั้งจริงในคอนเทนเนอร์) พร้อมไฟล์ config ตัวอย่างเต็ม (`~/.claude.json`, `.mcp.json`, `--mcp-config`, Codex `config.toml`) และหมายเหตุ Windows (ติดป้ายยังไม่ได้ทดลอง)
