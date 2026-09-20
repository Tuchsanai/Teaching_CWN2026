# เรียนรู้ Model Context Protocol (MCP): จากแนวคิดพื้นฐานสู่การสร้าง MCP Server ของตัวเอง

บทเรียนนี้ต่อจากบทที่ 02 (Loop / Graph / Dynamic Workflow) ซึ่งนักศึกษาเขียน Prompt ให้ AI ทำงานเป็นเวิร์กโฟลว์ คราวนี้เราจะดูว่า **AI Agent ไปทำงานกับโลกภายนอกได้อย่างไร** เช่น วาดรูปลง canvas, ควบคุมเบราว์เซอร์, หรือเรียกโค้ด Python ของเรา คำตอบคือ **Model Context Protocol (MCP)** มาตรฐานเปิดที่ทำให้ AI ค้นพบและเรียกใช้เครื่องมือภายนอกได้โดยไม่ต้องเขียนตัวเชื่อมใหม่ทุกครั้ง

บทเรียนแบ่งเป็น 8 บท: ทฤษฎี (บทที่ 1–3) → ติดตั้งทุกอย่างด้วยพรอมป์ต์เดียว (บทที่ 4) → ใช้ MCP server ที่มีอยู่แล้ว (Case Study 1 Excalidraw MCP, Case Study 2 Playwright MCP) → สร้าง MCP server เอง (บทที่ 7) → สรุปและงานส่ง (บทที่ 8) **ทุกภาพในบทเรียนวาดด้วย Excalidraw MCP โดย AI Agent** และ**ตัวเลข ข้อความ error และผลลัพธ์ในส่วนบันทึกการทดลองมาจากการรันจริง**บนเครื่องเรียนเมื่อวันที่ 19 กันยายน 2026 เก็บไว้ใน `lab-results/`

![แผนที่บทเรียน 03_MCP วาดด้วย Excalidraw MCP](img/d08-lesson-map.png)

**เลือกอ่าน:** [เตรียมตัวและงานส่ง](#prep) · [บทที่ 1 MCP คืออะไร](#ch1) · [บทที่ 2 โครงสร้าง](#ch2) · [บทที่ 3 MCP vs Function vs API](#ch3) · [บทที่ 4 ติดตั้ง](#ch4) · [บทที่ 5 Excalidraw MCP](#ch5) · [บทที่ 6 Playwright MCP](#ch6) · [บทที่ 7 สร้าง MCP server](#ch7) · [บทที่ 8 สรุป](#ch8) · [ภาคผนวก](#appendix)

<a id="prep"></a>
## สิ่งที่ต้องเตรียม และสิ่งที่ต้องส่ง

**เครื่องมือที่ใช้ในบทเรียนนี้ (เวอร์ชันที่ทดลองจริง)**

| เครื่องมือ | เวอร์ชัน | ใช้ทำอะไร |
| --- | --- | --- |
| Claude Code | 2.1.258 | Host ของ MCP (AI Agent ที่นักศึกษาสั่งงาน) |
| Node.js | v24.20.0 | รัน MCP server ที่เขียนด้วย JavaScript |
| `mcp-excalidraw-server` | 2.0.0 | Excalidraw MCP (Case Study 1) |
| `@playwright/mcp` | 0.0.80 | Playwright MCP (Case Study 2) ต่อ headless Chrome 153 ผ่าน CDP |
| Python | 3.12.3 (`/opt/venv/bin/python`) | เขียน MCP server เองและเว็บทดลอง |
| `mcp` (Python SDK) | 2.0.0 (รองรับ spec 2026-07-28) | สร้าง MCP server / client |
| `kokoro` | 0.9.4 (+ `espeak-ng` 1.51) | สังเคราะห์เสียงภาษาอังกฤษในเว็บทดลอง |
| FastAPI / uvicorn | 0.136.3 / 0.52.4 | เว็บทดลอง Kokoro TTS |

**ติดตั้งด้วยการส่งลิงก์ repo ต้นทาง ไม่ต้องตั้งค่าเอง**: สิ่งเดียวที่ต้องมีก่อนคือ Claude Code ที่ล็อกอินแล้ว (จากบทที่ 01) กับ Node.js และ Python 3 ในเครื่อง จากนั้นเปิด `claude` แล้วส่ง **ลิงก์ GitHub ของเครื่องมือพร้อมคำขอสั้น ๆ** (บทที่ 4.2.1 หรือไฟล์ [`labs/prompts/setup-00-all-in-one.md`](labs/prompts/setup-00-all-in-one.md)) AI จะอ่าน README ของ repo เลือกวิธีติดตั้งเอง ตั้งค่า MCP ให้ Host และทดสอบจนใช้งานได้ (Kokoro ใช้ CPU ได้ ไม่จำเป็นต้องมี GPU และเป็นไลบรารี ไม่ใช่ MCP server สำเร็จรูป)

**ใช้ Codex CLI ได้เช่นกัน:** เปิด `codex` แล้วใช้คำขอในข้อ 4.2.2 หรือ [`setup-00-codex.md`](labs/prompts/setup-00-codex.md) ซึ่งใช้ repo ต้นทางชุดเดียวกัน ต่างเฉพาะ Host ที่ให้ตั้งค่า จากนั้นเปิด session ใหม่และทดสอบด้วย S5 (หลักฐานการรันจริงในบทเรียนนี้มาจาก Claude Code ยังไม่มีผลรันฝั่ง Codex)

**งานที่นักศึกษาต้องส่ง** (เกณฑ์ละเอียดอยู่ในบทที่ 8)

1. Lab 5: ภาพจาก Excalidraw MCP อย่างน้อย 3 ภาพ (architecture, workflow, flow) + ภาพที่แก้จาก Prompt 1 ภาพ + บันทึกลำดับ tool ที่ AI เรียก
2. Lab 6: screenshot ชุดของการควบคุมเว็บ Kokoro ผ่าน Playwright MCP + snapshot + บันทึกขั้นตอน
3. Lab 7: MCP server ของตัวเอง (มี tool ที่เพิ่มเองอย่างน้อย 1 ตัว) + wire log + ผลที่ Claude Code เรียก tool ได้จริง
4. รายงานสั้น 1 หน้า: MCP แก้ปัญหาอะไร และสิ่งที่ค้นพบระหว่างทดลอง (ต้องอ้างไฟล์หลักฐานของตัวเอง)

---

<a id="ch1"></a>
## บทที่ 1 MCP คืออะไร และถูกสร้างมาเพื่อแก้ปัญหาอะไร

### 1.1 ปัญหาก่อนมี MCP: ทุกแอปต้องเขียนตัวเชื่อมกับทุกเครื่องมือ

LLM (เช่น Claude) เก่งเรื่องอ่านและเขียนข้อความ แต่ **ทำอะไรกับโลกภายนอกไม่ได้เอง** มันไม่รู้เวลาปัจจุบัน วาดรูปลง canvas ไม่ได้ กดปุ่มบนเว็บไม่ได้ และเรียกฟังก์ชัน Python ของเราไม่ได้ วิธีที่ใช้กันคือ "tool calling": โปรแกรมที่ครอบ LLM (เรียกว่า Host เช่น Claude Code, Codex CLI, หรือแอปที่เราเขียนเอง) บอก LLM ว่ามีเครื่องมืออะไรบ้าง แล้ว LLM ตอบกลับว่าอยากเรียกเครื่องมือไหนด้วย argument อะไร

ปัญหาคือ **แต่ละ Host ต้องเขียนโค้ดเชื่อมกับแต่ละเครื่องมือเอง** ถ้ามีแอป AI 3 ตัว และเครื่องมือ 4 อย่าง ต้องเขียนตัวเชื่อม 3 × 4 = 12 ชุด ต่างคนต่างกำหนดรูปแบบ ต่างคนต่างดูแล เพิ่มเครื่องมือใหม่ 1 อย่างต้องแก้ทุกแอป

![ภาพเปรียบเทียบก่อนและหลังมี MCP: N×M integration กับ N+M](img/d01-nxm-problem.png)

*ซ้าย: ก่อนมี MCP แอป 3 ตัว × เครื่องมือ 4 อย่าง = ตัวเชื่อม 12 ชุด · ขวา: หลังมี MCP ทุกฝ่ายพูดโปรโตคอลเดียวกัน เหลือ 3 + 4 = 7 การเชื่อมต่อ*

### 1.2 MCP คืออะไร

**Model Context Protocol (MCP)** คือโปรโตคอลเปิด (open protocol) ที่ Anthropic เผยแพร่ในเดือนพฤศจิกายน 2024 และปัจจุบันดูแลโดยชุมชนที่ [modelcontextprotocol.io](https://modelcontextprotocol.io) สเปกฉบับล่าสุดที่ใช้ในบทเรียนนี้คือรุ่น **2026-07-28** ซึ่งนิยามไว้ว่า

> MCP is an open protocol that enables seamless integration between LLM applications and external data sources and tools.

หัวใจของ MCP มี 3 อย่าง

1. **ภาษากลางแบบเดียว** — ทุกข้อความเป็น [JSON-RPC 2.0](https://www.jsonrpc.org/) (JSON ที่มี `method`, `params`, `id`, `result`)
2. **การค้นพบอัตโนมัติ** — server "ประกาศ" ว่ามีเครื่องมืออะไร รับ argument แบบไหน (`tools/list`) โดย Host ไม่ต้องรู้ล่วงหน้า
3. **แยกบทบาทชัดเจน** — Host/Client เป็นฝั่ง AI, Server เป็นฝั่งเครื่องมือ ใครเขียนฝั่งไหนก็ได้ ภาษาอะไรก็ได้

สเปกเปรียบ MCP กับ Language Server Protocol (LSP) ที่ทำให้ editor ทุกตัวรองรับภาษาโปรแกรมได้ผ่านมาตรฐานเดียว หลายคนจึงเรียก MCP ว่า "USB-C ของ AI"

### 1.3 ทำไม AI Agent / LLM จึงต้องใช้ MCP

| ถ้าไม่มี MCP | เมื่อมี MCP |
| --- | --- |
| ต้องเขียนโค้ดบอก LLM เองว่า tool แต่ละตัวชื่ออะไร รับ argument อะไร | Host เรียก `tools/list` แล้วได้ชื่อ คำอธิบาย และ `inputSchema` (JSON Schema) จาก server อัตโนมัติ |
| ต้องเขียน glue code แปลงคำตอบของ LLM ไปเรียก API จริง | Host ส่ง `tools/call {name, arguments}` ตามมาตรฐาน server ทำงานแล้วตอบ `result` |
| เครื่องมือที่ทำให้ Claude Code ใช้ ไม่ได้ทำให้ Codex ใช้ | server เดียวใช้ได้กับทุก Host ที่พูด MCP (บทเรียนนี้ใช้ Excalidraw MCP และ Playwright MCP ตัวเดียวกันทั้งใน Claude Code และ Codex) |
| ไม่มีจุดกลางสำหรับขออนุมัติผู้ใช้ | สเปกกำหนดให้ Host ถามผู้ใช้ก่อนเรียก tool ("there SHOULD always be a human in the loop") |

ตัวอย่างในบทเรียนนี้เอง: **แผนภาพทั้ง 9 ภาพวาดโดย AI Agent (Claude Code) ผ่าน Excalidraw MCP** และ **การกรอกฟอร์มบนเว็บ Kokoro ทำผ่าน Playwright MCP** โดยผู้สอนไม่ได้เขียนโค้ดเชื่อม Excalidraw หรือเบราว์เซอร์กับ Claude เลย เพียงตั้งค่าให้ Claude Code รู้จัก MCP server สองตัวนี้

### 1.4 สิ่งที่ MCP ไม่ใช่

- ไม่ใช่โมเดล AI และไม่ใช่ agent framework — เป็นแค่ "ภาษากลาง" ระหว่าง AI กับเครื่องมือ
- ไม่ได้มาแทน REST API หรือ Python function — แต่ครอบของเดิมให้ AI ค้นพบและเรียกได้ (ดูบทที่ 3)
- ไม่ได้ทำให้ AI ทำอะไรก็ได้ — Host ยังเป็นผู้คุมสิทธิ์และผู้ใช้เป็นผู้อนุมัติ

---

<a id="ch2"></a>
## บทที่ 2 โครงสร้างการทำงานของ MCP

### 2.1 Host, MCP Client, MCP Server, Tools / Resources / Prompts

![โครงสร้าง MCP บนเครื่องเรียน: Host → MCP Client → MCP Server → เครื่องมือจริง](img/d02-mcp-architecture.png)

| องค์ประกอบ | หน้าที่ | ตัวอย่างจริงในบทเรียนนี้ |
| --- | --- | --- |
| **Host** | โปรแกรม AI ที่ผู้ใช้ใช้ สร้างและจัดการ MCP Client, คุมสิทธิ์, ถามผู้ใช้ก่อนเรียก tool, รวมผล tool กลับเข้า LLM | Claude Code 2.1.258, Codex CLI 0.154 |
| **LLM** | อ่านรายการ tool ใน context แล้วตัดสินใจว่าจะเรียก tool ใดด้วย argument อะไร | claude-sonnet-5 (รอบทดสอบบทที่ 7), Claude Fable 5.1 (รอบวาดภาพและ Playwright) |
| **MCP Client** | ตัวเชื่อม 1 ตัวต่อ 1 server อยู่ใน Host ส่ง/รับ JSON-RPC | Claude Code สร้าง client ให้ `excalidraw`, `playwright`, `hello-lab`, `kokoro-tts` |
| **MCP Server** | process แยก ประกาศ Tools / Resources / Prompts และทำงานจริงกับเครื่องมือ | `mcp-excalidraw-server` (Node), `playwright-mcp` (Node), `hello_server.py` และ `tts_server.py` (Python) |
| **Tools** | ฟังก์ชันให้โมเดลเรียก (model-controlled) มีชื่อ คำอธิบาย `inputSchema` | `batch_create_elements`, `browser_click`, `add(a, b)`, `speak(text, voice)` |
| **Resources** | ข้อมูลให้อ่าน ระบุด้วย URI | `lab://info` ของ hello-lab |
| **Prompts** | แม่แบบข้อความที่ server เตรียมไว้ | `explain_mcp(topic)` ของ hello-lab |

กติกาสำคัญจากสเปก (หน้า Architecture):

- "Each client is created by the host and communicates with exactly one server" — 1 Client ต่อ 1 Server
- "Servers should be extremely easy to build" — server เล็ก ๆ ทำงานอย่างเดียว Host เป็นคนจัดการเรื่องยาก
- "Servers should not be able to read the whole conversation, nor 'see into' other servers" — server เห็นเฉพาะ argument ที่ถูกส่งมา ไม่เห็นบทสนทนา

### 2.2 ลำดับข้อความเมื่อผู้ใช้สั่งงาน 1 ครั้ง

![ลำดับข้อความ MCP: Prompt → Agent → Client → Server → Tool](img/d03-mcp-sequence.png)

ข้อความในภาพเป็น JSON-RPC จริง ด้านล่างคือข้อความที่**ดักได้จากสายจริง**ระหว่าง Python client กับ `hello_server.py` (ไฟล์ [`wire-hello.jsonl`](lab-results/own-server/run-2026-09-19-062712/wire-hello.jsonl) ตัดให้สั้น)

**Client ขอรายการ tool (`tools/list`)**

```json
{"jsonrpc": "2.0", "id": 2, "method": "tools/list",
 "params": {"_meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28",
                      "io.modelcontextprotocol/clientInfo": {"name": "mcp", "version": "0.1.0"}}}}
```

**Server ตอบรายการ tool พร้อม `inputSchema` ที่สร้างจาก type hint ของ Python**

```json
{"jsonrpc": "2.0", "id": 2, "result": {"resultType": "complete", "tools": [
  {"name": "add",
   "description": "บวกเลขจำนวนเต็มสองจำนวน / Add two integers and return the sum.",
   "inputSchema": {"type": "object",
                   "properties": {"a": {"title": "A", "type": "integer"}, "b": {"title": "B", "type": "integer"}},
                   "required": ["a", "b"]},
   "outputSchema": {"type": "object", "properties": {"result": {"type": "integer"}}, "required": ["result"]}},
  ...]}}
```

**Client เรียก tool (`tools/call`) และ Server ตอบผล**

```json
{"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "add", "arguments": {"a": 17, "b": 25}, "_meta": {...}}}
{"jsonrpc": "2.0", "id": 5, "result": {"content": [{"type": "text", "text": "42"}], "isError": false,
                                       "resultType": "complete", "structuredContent": {"result": 42}}}
```

สังเกตว่า `tools/list` เกิดครั้งเดียวตอนต่อ server ส่วน `tools/call` เกิดทุกครั้งที่ LLM เลือกใช้ tool และผลลัพธ์กลับมาใน `content` (ข้อความ/รูป/เสียง) กับ `structuredContent` (JSON ตาม `outputSchema`) ถ้า tool ทำงานไม่สำเร็จ server ตอบ `isError: true` พร้อมข้อความให้ LLM แก้ตัวได้ (ต่างจาก JSON-RPC error ที่แปลว่า request ผิดรูป)

### 2.3 Transport: stdio และ Streamable HTTP

โปรโตคอลเหมือนกันทุก transport ต่างกันแค่ "วิธีส่งข้อความ"

| Transport | วิธีทำงาน | ใช้เมื่อ | ตัวอย่างในบทเรียน |
| --- | --- | --- | --- |
| **stdio** | Host เปิด server เป็น subprocess แล้วส่ง JSON-RPC ทีละบรรทัดผ่าน stdin/stdout (stderr ไว้ log) | server อยู่บนเครื่องเดียวกัน (กรณีส่วนใหญ่) | Excalidraw MCP, Playwright MCP, `hello_server.py` |
| **Streamable HTTP** | server เปิด endpoint เดียว (เช่น `/mcp`) client ส่ง HTTP POST ทีละข้อความ คำตอบเป็น JSON หรือ SSE stream | server อยู่คนละเครื่อง/บริการกลาง | `hello_server.py --http` ที่ `http://127.0.0.1:8766/mcp` (บทที่ 7.6) |

ข้อควรจำของ stdio: **ห้าม `print()` ลง stdout ใน server** เพราะ stdout คือช่องส่ง JSON-RPC ถ้าอยาก log ให้เขียนไป stderr

### 2.4 เวอร์ชันโปรโตคอลที่พบจริงบนสาย

สเปก MCP ปรับใหญ่ในรุ่น 2026-07-28: ทุก request แนบเวอร์ชันและ capability ของ client มาใน `_meta` และมี `server/discover` สำหรับถาม capability ของ server แทน handshake `initialize` แบบเดิม แต่รุ่นเก่ายังต้องใช้งานได้ ผลที่ดักได้จากสายในบทที่ 7 ยืนยันเรื่องนี้

| Client | ข้อความแรกที่ส่ง | เวอร์ชันที่ประกาศ | หลักฐาน |
| --- | --- | --- | --- |
| Python SDK `mcp` 2.0.0 (`mcp.Client`) | `server/discover` (ไม่มี `initialize`) แล้วต่อด้วย `tools/list` | `_meta.io.modelcontextprotocol/protocolVersion = "2026-07-28"` ทุก request | [`wire-hello.jsonl`](lab-results/own-server/run-2026-09-19-062712/wire-hello.jsonl) |
| Claude Code 2.1.258 | `initialize` → `notifications/initialized` → `tools/list`, `prompts/list`, `resources/list` | `protocolVersion: "2025-11-25"`, `clientInfo: {"name": "claude-code", "version": "2.1.258"}` | [`claude-use-wire-hello.jsonl`](lab-results/own-server/run-2026-09-19-062712/claude-use-wire-hello.jsonl) |

server ตัวเดียวกัน (`hello_server.py` ที่เขียนด้วย SDK 2.0) ตอบได้ทั้งสองแบบ นี่คือข้อดีของการใช้ SDK: เรื่องเวอร์ชันและ transport SDK จัดการให้

---

<a id="ch3"></a>
## บทที่ 3 MCP ต่างจากการเรียก Python Function หรือ API โดยตรงอย่างไร

ใช้งานเดียวกันตลอดบทเรียน: **สังเคราะห์เสียงภาษาอังกฤษด้วย Kokoro-82M** เราเปิดความสามารถนี้ให้เรียกได้ 3 แบบ โดยโค้ด Kokoro ไม่ต้องแก้เลย

![งานเดียวกันเรียกได้ 3 แบบ: Python function, REST API, MCP tool](img/d04-three-ways.png)

**แบบที่ 1 — Python function** ([`labs/kokoro-web/kokoro_core.py`](labs/kokoro-web/kokoro_core.py))

```python
def synthesize(text: str, voice: str = "af_heart") -> dict:
    """แปลงข้อความภาษาอังกฤษเป็นไฟล์เสียง .wav"""
    ...
    return {"path": str(path), "duration_sec": ..., "sample_rate": 24000, "gen_ms": gen_ms, "voice": voice}
```

ใครเรียกได้: เฉพาะโค้ด Python ใน process เดียวกัน (`from kokoro_core import synthesize`)

**แบบที่ 2 — REST API ด้วย FastAPI** ([`labs/kokoro-web/app.py`](labs/kokoro-web/app.py))

```python
@app.post("/api/tts")
async def tts(req: TTSRequest):
    result = await run_in_threadpool(kokoro_core.synthesize, req.text, req.voice)
    return {"audio_url": f"/audio/{result['filename']}", "duration_sec": result["duration_sec"], ...}
```

ใครเรียกได้: ทุกโปรแกรมที่ส่ง HTTP ได้ (เบราว์เซอร์, curl, แอปอื่น) ผลจริงจาก curl: [`web-curl-tts.json`](lab-results/own-server/run-2026-09-19-062712/web-curl-tts.json) ได้เสียงยาว 3.98 วินาที ใช้เวลาสร้าง 672 ms บน CPU · ส่งข้อความว่างได้ `{"error":"text must not be empty"}` HTTP 400 ([`web-curl-tts-empty.txt`](lab-results/own-server/run-2026-09-19-062712/web-curl-tts-empty.txt))

**แบบที่ 3 — MCP tool** ([`labs/my-mcp-server/tts_server.py`](labs/my-mcp-server/tts_server.py))

```python
mcp = MCPServer("kokoro-tts", instructions="แปลงข้อความภาษาอังกฤษเป็นไฟล์เสียง .wav ด้วย Kokoro-82M")

@mcp.tool()
def speak(text: str, voice: str = "af_heart") -> dict:
    """สังเคราะห์เสียงภาษาอังกฤษจากข้อความ แล้วคืน path ของไฟล์ .wav พร้อมความยาว (วินาที)"""
    r = kokoro_core.synthesize(text, voice)
    return {"path": r["path"], "duration_sec": r["duration_sec"], "sample_rate": r["sample_rate"], "gen_ms": r["gen_ms"], "voice": r["voice"]}
```

ใครเรียกได้: ทุก MCP host โดย LLM ค้นพบเองจาก `tools/list` ผลจริง: Claude Code เรียก `mcp__kokoro-tts__speak {"text": "Model Context Protocol lets one server serve many agents."}` แล้วได้ไฟล์เสียงยาว 4.45 วินาที ([`claude-tts-summary.md`](lab-results/own-server/run-2026-09-19-062712/claude-tts-summary.md))

**ตารางเปรียบเทียบ**

| ประเด็น | Python function | REST API | MCP tool |
| --- | --- | --- | --- |
| ใครเรียกได้ | โค้ดใน process เดียวกัน | ทุกโปรแกรมที่ส่ง HTTP ได้ | ทุก MCP host (Claude Code, Codex, แอปของคุณ) |
| LLM รู้จักได้เองไหม | ไม่ ต้องเขียนโค้ดเรียกเอง | ไม่ ต้องเขียน glue code + อธิบาย API ให้ LLM ทุกแอป | รู้ จาก `tools/list` + `inputSchema` อัตโนมัติ |
| รูปแบบข้อความ | การเรียกฟังก์ชัน | กำหนดเองต่อ API (path, JSON ต่างกัน) | มาตรฐานเดียว JSON-RPC 2.0 |
| การอนุมัติจากผู้ใช้ | ไม่มี | แล้วแต่แอป | Host ถามผู้ใช้ก่อนเรียก tool |
| ข้ามภาษา/ข้ามเครื่อง | ไม่ได้ | ได้ | ได้ (stdio ในเครื่อง, Streamable HTTP ข้ามเครื่อง) |
| เหมาะกับ | logic ภายในโปรแกรม | ให้บริการแอปอื่น/หน้าเว็บ | ให้ AI Agent ใช้เป็นเครื่องมือ |

สรุป: MCP ไม่ได้มาแทน function หรือ API แต่เป็น "ชั้นประกาศและเรียกใช้แบบมาตรฐาน" ที่ครอบของเดิม ในบทที่ 7 นักศึกษาจะเห็นว่าห่อ function เป็น MCP tool ใช้โค้ดเพิ่มไม่ถึง 20 บรรทัด

---

<a id="ch4"></a>
## บทที่ 4 ติดตั้งและตั้งค่า MCP ด้วยพรอมป์ต์ (ให้ AI ทำให้เอง)

### 4.1 เริ่มตรงนี้: ส่งลิงก์ repo ต้นทางให้ AI แล้วขอด้วยภาษาธรรมดา

ทักษะที่ต้องการจากบทนี้ไม่ใช่การท่องคำสั่งติดตั้ง แต่คือ **การส่งลิงก์ GitHub ของเครื่องมือ พร้อมบอกสั้น ๆ ว่าต้องการอะไร** แล้วให้ AI Host อ่าน README ของ repo นั้นเอง สำรวจว่ามีวิธีติดตั้งแบบใดบ้าง เลือกวิธีที่เหมาะกับเครื่องและ Host ที่ใช้อยู่ ตั้งค่า MCP ให้ แล้วทดสอบจนใช้งานได้จริง เพราะในงานจริงเครื่องมือใหม่จะออกมาเรื่อย ๆ และผู้สอนไม่สามารถแจกขั้นตอนสำเร็จรูปให้ทุกตัวได้

เครื่องมือ 3 ตัวที่บทนี้ใช้ และ repo ต้นทางที่ต้องส่งให้ AI

| เครื่องมือ | repo ต้นทาง | เป็นอะไรตามเอกสารต้นทาง |
| --- | --- | --- |
| Excalidraw MCP | <https://github.com/yctimlin/mcp_excalidraw> | เป็น MCP server พร้อมใช้ (แพ็กเกจ npm `mcp-excalidraw-server` ระบุ `repository.url` ชี้มา repo นี้) README บอกว่ามี 3 ทางเลือก: agent skill + CLI (`npx -y mcp-excalidraw-server <command>`), MCP server แบบ stdio, และ REST API — ให้ AI เลือกเองว่าจะใช้ทางไหนกับ Host ของเรา |
| Playwright MCP | <https://github.com/microsoft/playwright-mcp> | MCP server ควบคุมเบราว์เซอร์ของ Microsoft ใช้ accessibility snapshot แทนภาพ README มีคำสั่งเพิ่ม server ให้ทั้ง Claude Code และ Codex อยู่แล้ว |
| Kokoro TTS | <https://github.com/hexgrad/kokoro> | **เป็นไลบรารี TTS (Python) ไม่ใช่ MCP server** README เป็นวิธี `pip install kokoro` แล้วเรียก `KPipeline` ในโค้ด ไม่มี MCP server มาให้ ถ้าต้องการใช้ผ่าน MCP ต้องให้ AI **เขียน wrapper ห่อเป็น MCP server เอง** (ดูข้อ 4.3.3 และบทที่ 7) |

> ข้อมูลในตารางนี้มาจากการเปิดอ่าน README ของ repo ต้นทางและข้อมูลแพ็กเกจ npm แบบอ่านอย่างเดียวเมื่อ 20 กันยายน 2026 ไม่ได้ติดตั้งหรือรันซ้ำในรอบนี้ ถ้า README ต้นทางเปลี่ยน ให้เชื่อ README ก่อนเอกสารนี้ และนี่คือเหตุผลที่บทเรียนให้ AI ไปอ่าน README เองทุกครั้ง

**ทำตาม 3 ขั้นตอนนี้**

1. เปิดเทอร์มินัลในโฟลเดอร์ทำงานของตัวเอง แล้วเปิด Host ที่ติดตั้งและล็อกอินไว้แล้วจากตารางด้านล่าง
2. ส่ง **คำขอภาษาธรรมดา + ลิงก์ repo** ตามข้อ 4.2 ให้ตรงกับ Host ที่ใช้ แล้วให้ AI อ่าน README ติดตั้ง ตั้งค่า และรายงานผล
3. เมื่อจบ เปิด Host เป็น session ใหม่ แล้วใช้ **Prompt S5** ในข้อ 4.4.1 ทดสอบว่าเรียก tool ได้จริง

| ใช้โปรแกรมไหน | คำสั่งเปิด | คำขอที่ใช้ |
| --- | --- | --- |
| Claude Code | `claude` | ข้อ 4.2.1 |
| Codex CLI | `codex` | ข้อ 4.2.2 |

สอง Host นี้ใช้ **repo ต้นทางชุดเดียวกัน** ต่างกันเฉพาะว่าให้ AI ตั้งค่า MCP ให้ Host ตัวไหน (`claude mcp add` / `~/.claude.json` เทียบกับ `codex mcp add` / `~/.codex/config.toml`) ซึ่ง AI จะหาวิธีที่ถูกต้องจาก README ของ repo และเอกสารของ Host เอง

**สิ่งที่ต้องมีก่อน:** Host ที่ล็อกอินแล้ว, Node.js (Excalidraw MCP รุ่น 2.0 ต้องการ Node ≥ 20 ตาม README ต้นทาง, Playwright MCP ระบุ Node ≥ 18) และ Python 3.10 ขึ้นไปถ้าจะทำส่วน Kokoro **ไม่ต้องมีโค้ดแล็บใด ๆ ของบทเรียนก่อน** ทั้ง `labs/kokoro-web` และ `labs/my-mcp-server` เป็นแล็บต่อเนื่องในข้อ 4.3.4 และบทที่ 7 ไม่ใช่เงื่อนไขเริ่มต้นของการติดตั้งเครื่องมือภายนอก

**ทำไมให้ AI ติดตั้งได้?** Host คือโปรแกรมที่เราใช้คุยกับ AI เช่น Claude Code หรือ Codex CLI ซึ่งเรียกใช้เทอร์มินัลได้ บน Linux/macOS มักใช้ Bash ดังนั้น AI จึงอ่าน README รันคำสั่งติดตั้ง ตั้งค่า MCP และตรวจผลให้ได้ ภายใต้สิทธิ์ที่ Host อนุญาต

**เมื่อพร้อมเรียนต่อ:** ต้องส่งออกภาพจาก Excalidraw ได้, เปิดเว็บจริงด้วย Playwright ได้ และสร้างไฟล์เสียงที่เปิดฟังได้จาก Kokoro การมีชื่อ server อยู่ในรายการเพียงอย่างเดียวยังไม่ยืนยันว่าเรียก tool สำเร็จ

| คำขอ/พรอมป์ต์ | ทำอะไร | อยู่ที่ |
| --- | --- | --- |
| **S0 (Claude Code)** | ส่ง 3 ลิงก์ ให้ Claude Code อ่าน README ติดตั้ง ตั้งค่า และทดสอบเอง | ข้อ 4.2.1 / [`setup-00-all-in-one.md`](labs/prompts/setup-00-all-in-one.md) |
| **S0 (Codex CLI)** | คำขอเดียวกัน แต่ให้ตั้งค่าเข้ากับ Codex | ข้อ 4.2.2 / [`setup-00-codex.md`](labs/prompts/setup-00-codex.md) |
| S1 Excalidraw MCP | ติดตั้ง/ตั้งค่าเฉพาะ Excalidraw จาก repo ต้นทาง | ข้อ 4.3.1 / [`setup-01-excalidraw.md`](labs/prompts/setup-01-excalidraw.md) |
| S2 Playwright MCP | ติดตั้ง/ตั้งค่าเฉพาะ Playwright จาก repo ต้นทาง | ข้อ 4.3.2 / [`setup-02-playwright.md`](labs/prompts/setup-02-playwright.md) |
| S3 Kokoro TTS | ใช้ไลบรารี Kokoro และให้ AI ห่อเป็น MCP server เอง | ข้อ 4.3.3 / [`setup-03-kokoro-web.md`](labs/prompts/setup-03-kokoro-web.md) |
| S4 แล็บต่อเนื่องของบทเรียน | ใช้โค้ดแล็บ `hello-lab`, `kokoro-tts`, เว็บ Kokoro ที่เตรียมไว้ (ทำหลังติดตั้งเครื่องมือหลัก) | ข้อ 4.3.4 / [`setup-04-own-server.md`](labs/prompts/setup-04-own-server.md) |
| S5 ตรวจสอบ | ใน session ใหม่: เรียก tool ของทุก server จริง | ข้อ 4.4.1 / [`setup-05-verify.md`](labs/prompts/setup-05-verify.md) |
| S6 ถอน | ถอน MCP server ของบทเรียนและหยุดบริการที่เปิดไว้ | ข้อ 4.4.2 / [`setup-06-remove.md`](labs/prompts/setup-06-remove.md) |
| ทำเองด้วยคำสั่ง | คำสั่งครบทุกขั้นสำหรับคัดลอกวางในเทอร์มินัล + ไฟล์ config ตัวอย่างเต็ม (ส่วนอ้างอิงเสริม) | ข้อ 4.6 |

### 4.2 Setup Prompt S0 — คำขอภาษาธรรมดาพร้อมลิงก์ repo

#### 4.2.1 สำหรับ Claude Code

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

#### 4.2.2 สำหรับ Codex CLI

เปิด `codex` ในโฟลเดอร์ทำงาน แล้ววางข้อความนี้ ใช้ **repo ต้นทางชุดเดียวกับ 4.2.1** ต่างกันเฉพาะ Host ที่ให้ตั้งค่า ไฟล์พร้อมคัดลอก: [`setup-00-codex.md`](labs/prompts/setup-00-codex.md)

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

### 4.3 คำขอแยกทีละเครื่องมือ (ใช้เมื่อติดตั้งทีละตัว หรือซ่อมเฉพาะจุด)

หลักการเดียวกับ 4.2 คือ **ลิงก์ repo + คำขอสั้น ๆ + เกณฑ์ผ่าน** เปลี่ยนคำว่า "Claude Code" เป็น "Codex CLI" ได้ถ้าใช้ Host อีกตัว

#### 4.3.1 S1 — เฉพาะ Excalidraw MCP

```text
ช่วยติดตั้ง Excalidraw MCP จาก https://github.com/yctimlin/mcp_excalidraw ให้ Claude Code บนเครื่องนี้ใช้งานได้
อ่าน README ของ repo ก่อน แล้วบอกฉันว่ามีวิธีใช้กี่แบบ ต่างกันอย่างไร และเลือกแบบไหนให้เครื่องนี้เพราะอะไร จากนั้นติดตั้ง ตั้งค่าให้ Claude Code รู้จัก และบอกว่าต้องเปิดหน้า canvas ที่ URL ไหนก่อนถึงจะถ่ายภาพ/ส่งออกไฟล์ได้
ทดสอบด้วยการวาดกล่องข้อความ 1 กล่องแล้วส่งออกเป็น PNG รายงานชื่อ tool หรือคำสั่งที่ใช้ และ path ของไฟล์ที่สร้างจริง
```

**ตรวจอย่างไรว่าคำขอนี้ทำงานสำเร็จ**

**วิธีอ่านผล:** ตัวอย่างด้านล่างเป็น **ผลที่คาดหวัง (Expected output)** เพื่อใช้ตรวจงาน ไม่ใช่ผลรันใหม่หรือข้อความที่ Host ต้องตอบตรงทุกตัวอักษร ค่า path ชื่อไฟล์ และเวลาจะแตกต่างกันได้ ต้องมีผลจาก tool หรือไฟล์จริงรองรับคำว่า “ผ่าน”

**ทดสอบหลังติดตั้ง:** เปิด Host เป็น session ใหม่ เปิด canvas ตาม URL ที่ AI รายงาน (README ต้นทางระบุค่าเริ่มต้น `http://127.0.0.1:3000` และบอกว่าการถ่ายภาพต้องมีแท็บเบราว์เซอร์เปิด canvas อยู่) หรือให้ Playwright เปิดให้ถ้าเครื่องไม่มีจอ แล้ววางข้อความนี้

```text
ใช้ Excalidraw วาดกล่องข้อความ “MCP พร้อมใช้งาน” 1 กล่อง ถ่ายภาพตรวจ แล้วส่งออก PNG รายงานชื่อ tool และ path ของไฟล์ที่สร้างจริง
```

**ตัวอย่างผลที่ควรเห็น**

```text
สร้างกล่องบน canvas ได้
ถ่ายภาพ canvas → เห็นกล่องและข้อความ
ส่งออกภาพ → ได้ path ของ PNG ที่เปิดดูได้
```

**ผ่านเมื่อ:** เปิด PNG แล้วเห็นกล่องและข้อความที่ขอ หากเจอ `No frontend client connected` ให้เปิด canvas ก่อนแล้วลองใหม่ ถ้ามีเพียงรายการ tool แต่ไม่มีภาพ ยังไม่ผ่านการทดสอบส่งออก

#### 4.3.2 S2 — เฉพาะ Playwright MCP

```text
ช่วยติดตั้ง Playwright MCP จาก https://github.com/microsoft/playwright-mcp ให้ Claude Code บนเครื่องนี้ใช้งานได้
อ่าน README ของ repo ก่อน (มีหัวข้อสำหรับ Claude Code และ Codex โดยตรง) ตรวจว่าเครื่องนี้มีจอแสดงผลหรือไม่ และรันด้วยสิทธิ์อะไร แล้วเลือกตัวเลือกของ CLI ให้เหมาะ เช่น ตัวเลือกเลือกเบราว์เซอร์ โหมดไม่มีหน้าต่าง หรือการปิด sandbox เมื่อรันเป็น root — ให้ยืนยันชื่อตัวเลือกจากเอกสารต้นทาง อย่าเดา
ทดสอบด้วยการเปิด https://www.python.org ทำ accessibility snapshot และถ่าย screenshot รายงานชื่อหน้า หัวข้อหลัก และ path ของไฟล์ภาพ
```

**ตรวจอย่างไรว่าคำขอนี้ทำงานสำเร็จ**

**วิธีอ่านผล:** ตัวอย่างด้านล่างเป็น **ผลที่คาดหวัง (Expected output)** เพื่อใช้ตรวจงาน ไม่ใช่ผลรันใหม่หรือข้อความที่ Host ต้องตอบตรงทุกตัวอักษร ค่า path ชื่อไฟล์ และเวลาจะแตกต่างกันได้ ต้องมีผลจาก tool หรือไฟล์จริงรองรับคำว่า “ผ่าน”

**ทดสอบหลังติดตั้ง:** เปิด Host เป็น session ใหม่ แล้วทดสอบกับเว็บสาธารณะก่อน ยังไม่ต้องมีเว็บของบทเรียน

```text
ใช้ Playwright MCP เปิด https://www.python.org ทำ accessibility snapshot แล้วรายงานชื่อหน้า หัวข้อหลัก และถ่าย screenshot พร้อม path ของไฟล์
```

**ตัวอย่างผลที่ควรเห็น**

```text
browser_navigate → เปิดหน้าเว็บจริงได้ (ไม่ใช่หน้า error หรือ about:blank)
ชื่อหน้า: มีคำว่า Python
browser_snapshot → มี heading, ลิงก์เมนู และช่องค้นหาของเว็บ
browser_take_screenshot → ได้ไฟล์ภาพหน้าเว็บที่เปิดดูได้
```

**ผ่านเมื่อ:** เปิดเว็บสาธารณะได้จริง อ่าน snapshot ได้ และได้ screenshot ที่เปิดดูแล้วเป็นหน้าเว็บนั้นจริง หากเครือข่ายเข้าเว็บนี้ไม่ได้ ให้ใช้เว็บสาธารณะอื่นที่เข้าถึงได้แทนและระบุ URL ที่ทดสอบ

#### 4.3.3 S3 — Kokoro TTS: repo ที่ "ไม่มี MCP server" มาให้

Kokoro ที่ <https://github.com/hexgrad/kokoro> เป็น **ไลบรารีสำหรับสังเคราะห์เสียง** (inference library ของโมเดล Kokoro-82M) README ของมันแสดงการติดตั้งด้วย `pip install kokoro` แล้วเรียก `KPipeline` ในโค้ด Python พร้อมบันทึกไฟล์เสียงด้วย `soundfile` (ตัวอย่างใน README ใช้ sample rate 24000 และแนะนำติดตั้ง `espeak-ng` สำหรับคำนอกคลัง) **ไม่มี MCP server มาให้ในตัว repo** ดังนั้นห้ามเรียกมันว่า "Kokoro MCP server" และถ้าต้องการใช้ผ่าน MCP ต้องมีคนเขียน wrapper ห่อ ซึ่งในบทเรียนนี้เราให้ AI เขียนให้จากคำขอสั้น ๆ แล้วเราอ่านโค้ดที่ได้ — นี่คือกรณีที่พบบ่อยที่สุดในงานจริง

```text
ฉันอยากให้ Claude Code สร้างเสียงพูดจากข้อความได้ โดยใช้ Kokoro จาก https://github.com/hexgrad/kokoro
อ่าน README ของ repo ก่อน แล้วบอกฉันตรง ๆ ว่ามันให้ MCP server มาด้วยหรือไม่ ถ้าไม่มี ให้ทำสองอย่าง: (1) ติดตั้งไลบรารีใน virtual environment แยก อย่าลงทับ python ของระบบ และทดสอบด้วยสคริปต์สั้น ๆ ให้ได้ไฟล์เสียงก่อน (2) เขียน MCP server เล็ก ๆ ห่อความสามารถนี้ มี tool เดียวคือรับข้อความแล้วคืน path ของไฟล์เสียง ความยาว และ sample rate
บอกฉันด้วยว่าโค้ด wrapper อยู่ไฟล์ไหน ใช้ไลบรารีอะไร แล้วตั้งค่าให้ Claude Code เรียก tool นี้ได้ สุดท้ายทดสอบด้วยข้อความ "Hello students." และรายงาน path ไฟล์เสียงกับความยาวจากผลจริง
```

**ตรวจอย่างไรว่าคำขอนี้ทำงานสำเร็จ**

**วิธีอ่านผล:** ตัวอย่างด้านล่างเป็น **ผลที่คาดหวัง (Expected output)** เพื่อใช้ตรวจงาน ไม่ใช่ผลรันใหม่หรือข้อความที่ Host ต้องตอบตรงทุกตัวอักษร ค่า path ชื่อไฟล์ และเวลาจะแตกต่างกันได้ ต้องมีผลจาก tool หรือไฟล์จริงรองรับคำว่า “ผ่าน”

**ตัวอย่างผลที่ควรเห็น**

```text
คำตอบระบุชัดว่า repo นี้เป็นไลบรารี ไม่มี MCP server มาให้
ติดตั้งใน venv แยก และบอกไฟล์ wrapper ที่เขียนขึ้นพร้อมเหตุผลของการออกแบบ tool
เรียก tool ด้วย "Hello students." → ได้ path ของไฟล์ .wav
duration_sec: มากกว่า 0, sample_rate: 24000
```

**ผ่านเมื่อ:** เปิดไฟล์เสียงที่ได้แล้ว **ได้ยินเสียงพูดจริง** และอ่านโค้ด wrapper แล้วเข้าใจว่าใครเป็นคนเรียกโมเดล ถ้า AI รายงานว่า "ติดตั้ง Kokoro MCP server จาก repo แล้ว" ให้ถามกลับทันทีว่า server นั้นมาจากไหน เพราะ repo ต้นทางไม่ได้ให้มา ครั้งแรกที่สร้างเสียงจะช้ากว่าปกติเพราะต้องโหลดโมเดล

#### 4.3.4 S4 — แล็บต่อเนื่องของบทเรียน (`hello-lab`, `kokoro-tts`, เว็บ Kokoro)

ส่วนนี้ **ไม่ใช่เงื่อนไขเริ่มต้นของการติดตั้งเครื่องมือภายนอก** แต่เป็นแล็บต่อเนื่องเมื่อจะ "สร้าง MCP server เอง" ในบทที่ 7 และใช้เว็บทดลองในบทที่ 6 โฟลเดอร์ [`labs/my-mcp-server/`](labs/my-mcp-server/) มี `hello_server.py` และ `tts_server.py` ที่เขียนไว้แล้วเป็นตัวอย่างอ้างอิง ส่วน [`labs/kokoro-web/`](labs/kokoro-web/) คือเว็บ FastAPI ที่ใช้เป็นเป้าหมายให้ Playwright ควบคุม ถ้าเพิ่งเริ่มบทที่ 4 ให้ข้ามข้อนี้ไปก่อนได้

```text
ในโฟลเดอร์บทเรียน 03_MCP นี้มีโค้ดแล็บเตรียมไว้ที่ labs/my-mcp-server (hello_server.py, tts_server.py) และเว็บทดลองที่ labs/kokoro-web
ช่วยเตรียมให้ใช้งานได้โดยไม่แก้โค้ดในสองโฟลเดอร์นั้น: สร้าง virtual environment ที่ labs/.venv ติดตั้งแพ็กเกจที่โค้ดต้องใช้ (อ่านจากไฟล์เอง) ทดสอบ server ด้วย labs/my-mcp-server/client_test.py โดยยังไม่ผ่าน LLM ให้เห็น tools/list และผล add(17, 25) = 42 จากนั้นตั้งค่าให้ Claude Code รู้จัก server ทั้งสองตัว และเริ่มเว็บทดลองด้วย labs/kokoro-web/run.sh แล้วตรวจ health endpoint จนพร้อมใช้งาน
รายงานคำสั่งที่รันจริง ผลทดสอบ และปัญหาที่เจอตามจริง
```

**ตรวจอย่างไรว่าคำขอนี้ทำงานสำเร็จ**

**วิธีอ่านผล:** ตัวอย่างด้านล่างเป็น **ผลที่คาดหวัง (Expected output)** เพื่อใช้ตรวจงาน ไม่ใช่ผลรันใหม่หรือข้อความที่ Host ต้องตอบตรงทุกตัวอักษร ค่า path ชื่อไฟล์ และเวลาจะแตกต่างกันได้ ต้องมีผลจาก tool หรือไฟล์จริงรองรับคำว่า “ผ่าน”

**ทดสอบหลังติดตั้ง:** จากโฟลเดอร์ `03_MCP` ทดสอบ server โดยตรงก่อน (คำสั่งสำหรับ Linux/macOS)

```bash
labs/.venv/bin/python labs/my-mcp-server/client_test.py --server hello
labs/.venv/bin/python labs/my-mcp-server/client_test.py --server tts
curl -sS http://127.0.0.1:8765/api/health
```

จากนั้นเปิด Host เป็น session ใหม่ แล้ววางข้อความนี้

```text
ใช้ tool add ของ hello-lab บวก 17 กับ 25 แล้วใช้ tool speak ของ kokoro-tts สร้างเสียง “Hello students.” รายงาน tool ที่เรียก ผลบวก path ของไฟล์เสียง และความยาวจากผลจริง
```

**ตัวอย่างผลที่ควรเห็น**

```text
Python client: พบ add ใน tools/list และ add(17, 25) = 42
Python client ฝั่ง TTS: พบ speak และสร้างไฟล์เสียงได้
health ของเว็บ: ok = true, device = cpu
Host เรียก add: 42
Host เรียก speak: ได้ path ของ .wav และ duration_sec > 0
```

**ผ่านเมื่อ:** ทั้ง Python client และ Host เรียกได้จริง หาก client ผ่านแต่ Host หา tool ไม่พบ ให้ตรวจการตั้งค่าและเปิด session ใหม่ หาก TTS ขาดแพ็กเกจหรือโหลดโมเดลไม่ได้ ให้ทำ S3 ก่อนแล้วทดสอบซ้ำ ค่า `model_loaded` อาจเป็น false ก่อนสร้างเสียงครั้งแรก จึงไม่ควรตัดสินจากค่านี้เพียงอย่างเดียว

### 4.4 พรอมป์ต์ตรวจสอบและถอนการตั้งค่า

#### 4.4.1 S5 — ตรวจว่า MCP ทุกตัวใช้งานได้จริง (วางใน session ใหม่หลังติดตั้ง)

```text
ตรวจว่าเครื่องมือ MCP ที่ติดตั้งไว้ใช้งานได้จริง ทำตามลำดับและรายงานผลทุกข้อพร้อมชื่อ tool ที่เรียก
1. ใช้ Playwright MCP เปิด https://www.python.org ทำ accessibility snapshot และถ่าย screenshot รายงานชื่อหน้าและ path ของภาพ
2. ใช้ Playwright MCP เปิดหน้า canvas ของ Excalidraw ตาม URL ที่ server รายงาน แล้วคง tab นี้ไว้ (ถ้าเครื่องมีจอและเปิด URL นี้ไว้ในเบราว์เซอร์แล้ว ให้ข้ามข้อนี้)
3. ใช้ Excalidraw วาดกล่อง 3 กล่อง "Host" → "MCP Client" → "MCP Server" เชื่อมด้วยลูกศร แล้วถ่ายภาพ canvas และส่งออกเป็น PNG บอก path ของไฟล์ที่ได้
4. ใช้ Kokoro สร้างเสียงจากข้อความ "Hello from MCP." บอก path ของไฟล์เสียง ความยาว และ sample rate จากผลจริง
5. ถ้าทำแล็บต่อเนื่องในข้อ 4.3.4 ไว้ ให้เรียก tool add ของ hello-lab ด้วย a=17, b=25 (ต้องได้ 42) และเปิดเว็บ Kokoro ของบทเรียนด้วย Playwright กรอกข้อความ "Verify prompt works." กด Speak รอจน "สร้างเสียงสำเร็จ" แล้วอ่านความยาวเสียง ถ้ายังไม่ได้ทำแล็บนี้ ให้ข้ามและระบุว่า "ไม่อยู่ในขอบเขตรอบนี้"
6. สรุปเป็นตาราง: server, tool ที่เรียก, ผล, ผ่าน/ไม่ผ่าน ถ้าข้อใดไม่ผ่านให้คัดลอกข้อความ error จริง
```

ข้อ 2 คือเคล็ดลับสำคัญ: Excalidraw MCP ต้องมีแท็บเบราว์เซอร์เปิด canvas อยู่จึงจะถ่ายภาพ/ส่งออกได้ (README ต้นทางระบุไว้ตรง ๆ) แทนที่จะให้ผู้ใช้เปิดเอง เราให้ **Playwright MCP เปิดแท็บนั้นให้** จึงทำงานได้แม้บนเครื่องที่ไม่มีจอ

**ตรวจอย่างไรว่าพรอมป์ต์นี้ทำงานสำเร็จ**

**วิธีอ่านผล:** ตัวอย่างด้านล่างเป็น **ผลที่คาดหวัง (Expected output)** เพื่อใช้ตรวจงาน ไม่ใช่ผลรันใหม่หรือข้อความที่ Host ต้องตอบตรงทุกตัวอักษร ค่า path ชื่อไฟล์ และเวลาจะแตกต่างกันได้ ต้องมีผลจาก tool หรือไฟล์จริงรองรับคำว่า “ผ่าน”

**ตัวอย่างรายงานที่ควรได้หลังวาง S5**

| สิ่งที่ทดสอบ | ผลที่คาดหวัง | หลักฐานที่ต้องมี |
| --- | --- | --- |
| Playwright เปิดเว็บสาธารณะ | เปิด `https://www.python.org` ได้จริง | snapshot + screenshot ที่เป็นหน้าเว็บนั้น |
| Playwright เปิด canvas | หน้า canvas เปิดได้ | snapshot หรือ screenshot ของ canvas |
| Excalidraw วาดและส่งออก | เห็น 3 กล่องและลูกศรตามโจทย์ | PNG ที่เปิดดูได้ |
| Kokoro สร้างเสียง | ได้เสียงจากข้อความที่สั่ง | ไฟล์ WAV ที่เปิดฟังได้ + ความยาว > 0 |
| แล็บต่อเนื่อง (ถ้าทำ) | `add(17, 25) = 42` และเว็บแสดง “สร้างเสียงสำเร็จ” | ผลจาก tool + screenshot ของเว็บ |

**ผ่านเมื่อ:** สี่แถวแรกผ่านครบ (แถวสุดท้ายผ่านเฉพาะผู้ที่ทำแล็บต่อเนื่อง) หากแถวใดยังไม่รันหรือมี error ให้ระบุ “ยังไม่ทดสอบ” หรือ “ไม่ผ่าน” พร้อมสาเหตุ ไม่คัดลอกคำว่า “ผ่าน” จากตัวอย่าง หลังแก้แล้วทดสอบแถวที่มีปัญหาซ้ำ

#### 4.4.2 S6 — ถอนการตั้งค่าเมื่อจบบทเรียน

```text
ช่วยถอนการตั้งค่าของบทเรียน MCP นี้ออกจาก Host ที่ฉันใช้ โดยแตะเฉพาะรายการที่บทเรียนนี้เพิ่มเข้าไป (เช่น excalidraw, playwright, server ของ Kokoro และ server ของแล็บถ้าเคยเพิ่ม) ห้ามลบ server อื่นของฉัน
หยุดบริการที่เปิดค้างไว้จากแล็บด้วย เช่น canvas ของ Excalidraw และเว็บทดลอง Kokoro (ตรวจให้แน่ใจก่อนว่าเป็น process ที่บทเรียนเริ่มเอง) ไม่ต้องลบ virtual environment และแพ็กเกจที่ติดตั้ง แต่บอกคำสั่งลบไว้ให้ แล้วปิดท้ายด้วยรายการ MCP server ที่เหลืออยู่เพื่อยืนยัน
```

**ตรวจอย่างไรว่าพรอมป์ต์นี้ทำงานสำเร็จ**

**วิธีอ่านผล:** ตัวอย่างด้านล่างเป็น **ผลที่คาดหวัง (Expected output)** เพื่อใช้ตรวจงาน ไม่ใช่ผลรันใหม่หรือข้อความที่ Host ต้องตอบตรงทุกตัวอักษร ค่า path ชื่อไฟล์ และเวลาจะแตกต่างกันได้ ต้องมีผลจาก tool หรือไฟล์จริงรองรับคำว่า “ผ่าน”

**ทดสอบหลังถอน:** ตรวจรายการ server ด้วย `claude mcp list` หรือ `codex mcp list` ตาม Host ที่ใช้ และตรวจว่า process ของบริการที่เริ่มในแล็บหยุดแล้ว

```text
ไม่พบ server ของบทเรียนในรายการของ Host ที่ถอน
process ของ canvas และเว็บ Kokoro ที่เริ่มในแล็บหยุดแล้ว
virtual environment และไฟล์งานยังอยู่
```

**ผ่านเมื่อ:** ถอนเฉพาะ server ของบทเรียนและหยุดบริการของแล็บ โดย server อื่นยังอยู่ครบ หาก URL ของเว็บยังตอบ ให้ตรวจเจ้าของ process ก่อน เพราะอาจมีบริการอื่นใช้พอร์ตเดียวกัน ไม่หยุด process อื่นเพื่อให้ผลตรวจผ่าน

### 4.5 ถ้าติดตั้งแล้วใช้งานไม่ได้ ให้ตรวจตรงนี้

หลังติดตั้งให้เปิด Host เป็น session ใหม่แล้วใช้ S5 ตรวจจริง หากพบปัญหา ให้เริ่มจากข้อความ error และวิธีแก้ต่อไปนี้

| error ที่พบ | สาเหตุ | สิ่งที่ต้องบอก AI ให้ปรับ |
| --- | --- | --- |
| `Error: async initializeServer: Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome Run "npx playwright install chrome"` | `@playwright/mcp` 0.0.82 (เวอร์ชันที่ใช้ตอนทดลอง) ใช้ Google Chrome เป็นค่าเริ่มต้น แม้เราติดตั้ง chromium ไว้แล้ว | ให้ AI ตั้งค่าเบราว์เซอร์ให้ตรงกับที่ติดตั้งจริง เช่น `--browser chromium` (README ต้นทางระบุค่าที่รับได้ไว้ในตารางตัวเลือกของ CLI และตัวอย่าง Docker ของ repo ใช้ `--browser chromium`) |
| `Running as root without --no-sandbox is not supported. See https://crbug.com/638180.` | รันเป็น root (คอนเทนเนอร์/เซิร์ฟเวอร์) Chromium ไม่ยอมเปิด sandbox | เพิ่ม `--no-sandbox` เมื่อรันเป็น root (AI ในรอบทดสอบแก้ `~/.claude.json` ให้เองแล้วขอ session ใหม่) |
| `No frontend client connected. Open the canvas in a browser first.` (Excalidraw) | ยังไม่มีแท็บเปิด canvas | S5 ข้อ 2 ให้ Playwright MCP เปิด URL ของ canvas (ค่าเริ่มต้นตาม README ต้นทางคือ `http://127.0.0.1:3000`) ก่อนวาด |

สำหรับ Codex ใช้ `codex mcp get <ชื่อ server>` ตรวจค่าที่ลงทะเบียน และ `/mcp` ใน session ดู server ที่ใช้งานอยู่ จากนั้นเรียก tool ซ้ำเพื่อยืนยันผล ส่วน Claude Code ใช้ `claude mcp list` แล้วทดสอบด้วย S5 เช่นกัน

ข้อความ error ทั้งสามแถวมาจากการทดลองติดตั้งจริงเมื่อ 19 กันยายน 2026 ด้วย Claude Code บันทึกเก็บไว้ใน [`lab-results/setup-prompt/run-2026-09-19-072524/`](lab-results/setup-prompt/run-2026-09-19-072524/) สำหรับผู้ที่ต้องการดูรายละเอียด (ยังไม่มีผลรันฝั่ง Codex)

### 4.6 คำสั่งติดตั้งและตั้งค่าแบบทำเอง (ครบทุกขั้น คัดลอกวางในเทอร์มินัลได้)

**ส่วนนี้เป็นข้อมูลอ้างอิงเสริม ไม่ใช่เส้นทางหลักของบทเรียน** เส้นทางหลักคือส่งลิงก์ repo ต้นทางพร้อมคำขอสั้น ๆ ตามข้อ 4.2–4.3 แล้วให้ AI อ่าน README และเลือกวิธีเอง คำสั่งชุดนี้เก็บไว้เพื่อ (1) ตรวจสอบย้อนหลังว่าในการติดตั้งจริงรอบก่อนเกิดอะไรขึ้น (คัดจาก [`setup-report.md`](lab-results/setup-prompt/run-2026-09-19-072524/setup-report.md) ที่ AI เขียนหลังติดตั้งจริงเมื่อ 19 กันยายน 2026) (2) ใช้เมื่ออยากทำเองทีละขั้น หรือใช้ Host ที่ไม่มี Bash ค่าและเวอร์ชันของแพ็กเกจอาจเปลี่ยนไปแล้ว ให้ยึด README ต้นทางเป็นหลักเสมอ ทุกคำสั่ง**รันจากโฟลเดอร์ `03_MCP`** บน Linux/macOS (Windows ดูข้อ 4.6.8)

#### 4.6.1 สิ่งที่ต้องมีก่อน (ครั้งเดียวต่อเครื่อง)

```bash
node -v && npm -v        # ต้อง v18 ขึ้นไป (บทเรียนทดสอบกับ v22 และ v24) — ถ้าไม่มี: ติดตั้ง Node.js LTS จาก https://nodejs.org หรือผ่าน nvm
python3 --version        # ต้อง 3.10 ขึ้นไป (บทเรียนทดสอบกับ 3.12) — Ubuntu: sudo apt-get install -y python3 python3-venv python3-pip
git --version
claude --version         # ต้องได้เลขเวอร์ชัน (บทเรียนทดสอบกับ 2.1.258 และ 2.1.278)
```

ถ้ายังไม่มี Claude Code ให้ติดตั้งแล้วล็อกอิน (รายละเอียดในบทที่ 01)

```bash
curl -fsSL https://claude.ai/install.sh | bash     # ติดตั้ง Claude Code (Linux/macOS) แล้วเปิดเทอร์มินัลใหม่
claude                                             # เปิดครั้งแรก แล้วพิมพ์ /login เพื่อล็อกอินด้วยบัญชี Claude
```

#### 4.6.2 Python virtual environment และแพ็กเกจ

```bash
python3 -m venv labs/.venv
labs/.venv/bin/pip install --upgrade pip
labs/.venv/bin/pip install "mcp[cli]" soundfile fastapi uvicorn
labs/.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu   # torch รุ่น CPU (ข้ามถ้ามี torch อยู่แล้ว) ~26 วินาทีในการทดสอบ
labs/.venv/bin/pip install kokoro                                                   # ~23 วินาที (โมเดล Kokoro-82M ดาวน์โหลดตอนใช้ครั้งแรก)
sudo apt-get update && sudo apt-get install -y espeak-ng                            # Linux (Debian/Ubuntu); macOS: brew install espeak-ng (แนวทาง — ยังไม่ได้ทดลอง)
labs/.venv/bin/pip list | grep -iE "^(mcp|kokoro|torch|fastapi|uvicorn|soundfile) "   # ตรวจเวอร์ชัน
```

#### 4.6.3 MCP server แบบ Node และเบราว์เซอร์ของ Playwright

```bash
npm install -g mcp-excalidraw-server @playwright/mcp     # ~53 วินาทีในการทดสอบ (เติม sudo ถ้า npm global ต้องใช้สิทธิ์)
npx playwright install chromium                          # ดาวน์โหลด Chromium ให้ Playwright (~30 วินาที)
sudo npx playwright install-deps chromium                # Linux เท่านั้น: ไลบรารีระบบที่ Chromium ต้องใช้ (~15 วินาที)
command -v mcp-excalidraw-server playwright-mcp          # ต้องพิมพ์ path ออกมาทั้งสองบรรทัด
```

#### 4.6.4 ลงทะเบียน MCP server กับ Claude Code

```bash
claude mcp add --scope user excalidraw -- mcp-excalidraw-server
claude mcp add --scope user playwright -- playwright-mcp --browser chromium                             # เครื่องที่มีจอแสดงผล
# claude mcp add --scope user playwright -- playwright-mcp --browser chromium --headless                # เครื่องไม่มีจอ (server / WSL ไม่มี GUI)
# claude mcp add --scope user playwright -- playwright-mcp --browser chromium --headless --no-sandbox   # รันเป็น root (container)
claude mcp add --scope user hello-lab  -- "$(pwd)/labs/.venv/bin/python" "$(pwd)/labs/my-mcp-server/hello_server.py"
claude mcp add --scope user kokoro-tts --env KOKORO_DEVICE=cpu -- "$(pwd)/labs/.venv/bin/python" "$(pwd)/labs/my-mcp-server/tts_server.py"
claude mcp list                 # ต้องเห็น ✔ Connected ทั้ง 4 ตัว
claude mcp get playwright       # ดูค่าที่ลงทะเบียนของตัวใดตัวหนึ่ง
# claude mcp remove playwright  # ถอนก่อนลงทะเบียนใหม่ (ชื่อซ้ำจะ error)
```

ตัวเลือก `--scope`: `user` = ใช้ได้ทุกโฟลเดอร์ (เก็บใน `~/.claude.json`), `project` = เก็บใน `.mcp.json` ของโฟลเดอร์ปัจจุบันเพื่อแชร์ผ่าน git (Claude Code จะถามอนุมัติครั้งแรกที่เปิด), `local` (ค่าเริ่มต้น) = เฉพาะโฟลเดอร์นี้บนเครื่องนี้

#### 4.6.5 เริ่มเว็บทดลองและทดสอบโดยไม่ใช้ LLM

```bash
PYTHON="$(pwd)/labs/.venv/bin/python" labs/kokoro-web/run.sh                     # เปิด http://127.0.0.1:8765 (pid ใน labs/kokoro-web/server.pid)
curl -s http://127.0.0.1:8765/api/health                                         # {"ok":true,"device":"cpu",...}
curl -s -X POST http://127.0.0.1:8765/api/tts -H "Content-Type: application/json" \
     -d '{"text":"Setup test from prompt.","voice":"af_heart"}'                  # ครั้งแรก ~3 วินาที (โหลดโมเดล) ครั้งต่อไปต่ำกว่า 1 วินาที
labs/.venv/bin/python labs/my-mcp-server/client_test.py --server hello           # ต้องเห็น tools/list และ add(17, 25) → 42
kill "$(cat labs/kokoro-web/server.pid)"                                         # หยุดเว็บเมื่อเลิกใช้
```

#### 4.6.6 ไฟล์ตั้งค่าที่คำสั่งด้านบนสร้างให้ (แก้เองได้)

ระดับผู้ใช้ `~/.claude.json` ส่วน `mcpServers` ตามรูปแบบที่การติดตั้งสร้างให้ (ค่าจริงหลังรันพรอมป์ต์ติดตั้งฉบับละเอียดในข้อ 4.6.9 เมื่อการทดสอบ 19 กันยายน 2026อยู่ใน [`container-state-after-s0.txt`](lab-results/setup-prompt/run-2026-09-19-072524/container-state-after-s0.txt) ซึ่งตอนนั้น `playwright` มี `args` เพียง `["--headless"]` ก่อนที่พรอมป์ต์จะถูกปรับให้ใส่ `--browser chromium`; แทน path ด้วยตัวยึด `<PATH_TO_03_MCP>`)

```json
{
  "mcpServers": {
    "excalidraw": {"type": "stdio", "command": "mcp-excalidraw-server", "args": [], "env": {}},
    "playwright": {"type": "stdio", "command": "playwright-mcp", "args": ["--browser", "chromium", "--headless"], "env": {}},
    "hello-lab":  {"type": "stdio", "command": "<PATH_TO_03_MCP>/labs/.venv/bin/python",
                   "args": ["<PATH_TO_03_MCP>/labs/my-mcp-server/hello_server.py"], "env": {}},
    "kokoro-tts": {"type": "stdio", "command": "<PATH_TO_03_MCP>/labs/.venv/bin/python",
                   "args": ["<PATH_TO_03_MCP>/labs/my-mcp-server/tts_server.py"], "env": {"KOKORO_DEVICE": "cpu"}}
  }
}
```

ระดับโปรเจกต์ `.mcp.json` (วางไว้ในโฟลเดอร์ `03_MCP` แล้ว commit ได้ รูปแบบเดียวกัน)

```json
{
  "mcpServers": {
    "excalidraw": {"command": "mcp-excalidraw-server", "args": []},
    "playwright": {"command": "playwright-mcp", "args": ["--browser", "chromium"]},
    "hello-lab":  {"command": "<PATH_TO_03_MCP>/labs/.venv/bin/python", "args": ["<PATH_TO_03_MCP>/labs/my-mcp-server/hello_server.py"]},
    "kokoro-tts": {"command": "<PATH_TO_03_MCP>/labs/.venv/bin/python", "args": ["<PATH_TO_03_MCP>/labs/my-mcp-server/tts_server.py"], "env": {"KOKORO_DEVICE": "cpu"}}
  }
}
```

ชั่วคราวเฉพาะคำสั่งเดียว (ไม่แตะการตั้งค่าเครื่อง ใช้เก็บหลักฐานในบทที่ 7): `claude -p --strict-mcp-config --mcp-config labs/my-mcp-server/mcp.json "<prompt>"` — ไฟล์ [`labs/my-mcp-server/mcp.json`](labs/my-mcp-server/mcp.json) เป็นตัวอย่างที่ห่อ server ด้วย `wire_capture.py` เพื่อดักข้อความบนสาย

```json
{
  "mcpServers": {
    "hello-lab": {
      "command": "/opt/venv/bin/python",
      "args": [".../wire_capture.py", "--log", ".../wire-claude-hello.jsonl", "--", "/opt/venv/bin/python", ".../hello_server.py"]
    },
    "kokoro-tts": {
      "command": "/opt/venv/bin/python",
      "args": [".../wire_capture.py", "--log", ".../wire-claude-tts.jsonl", "--", "/opt/venv/bin/python", ".../tts_server.py"],
      "env": {"KOKORO_DEVICE": "cpu"}
    }
  }
}
```

เมื่อต่อสำเร็จ Claude Code จะมองเห็น tool ในชื่อ `mcp__<ชื่อ server>__<ชื่อ tool>` เช่น `mcp__hello-lab__add` และ `mcp__kokoro-tts__speak` (ดู [`claude-discover-summary.md`](lab-results/own-server/run-2026-09-19-062712/claude-discover-summary.md)) ส่วน resource อ่านผ่านเครื่องมือกลาง `ReadMcpResourceTool {"server": "hello-lab", "uri": "lab://info"}`

#### 4.6.7 Codex CLI — คำสั่งติดตั้ง MCP และตรวจการตั้งค่า

หลังติดตั้งแพ็กเกจและสร้าง venv ตามข้อ 4.6.2–4.6.3 แล้ว รันจากโฟลเดอร์ `03_MCP` บน Linux/macOS:

```bash
codex mcp add excalidraw -- "$(command -v mcp-excalidraw-server)"
codex mcp add playwright -- "$(command -v playwright-mcp)" --browser chromium
# เครื่องไม่มีจอ: เติม --headless ต่อท้ายคำสั่ง playwright
# ถ้ารันเป็น root ใน container: เติม --headless --no-sandbox
codex mcp add hello-lab -- "$(pwd)/labs/.venv/bin/python" "$(pwd)/labs/my-mcp-server/hello_server.py"
codex mcp add kokoro-tts --env KOKORO_DEVICE=cpu -- "$(pwd)/labs/.venv/bin/python" "$(pwd)/labs/my-mcp-server/tts_server.py"
codex mcp list
codex mcp get playwright
```

เปิด `codex` เป็น session ใหม่ ใช้ `/mcp` ดู server ที่ใช้งานอยู่ แล้วใช้ S5 ทดสอบจริง `codex mcp list` แสดงค่าที่ลงทะเบียน ไม่ใช่หลักฐานว่าทุก tool ทำงานผ่านแล้ว

เมื่อต้องถอน ใช้ `codex mcp remove <ชื่อ server>` ทีละตัว ได้แก่ `excalidraw`, `playwright`, `hello-lab`, `kokoro-tts` ส่วนการหยุดเว็บ Kokoro ใช้ขั้นตอนเดียวกับ S6

รูปแบบคำสั่งอ้างอิง [เอกสาร MCP ของ OpenAI](https://developers.openai.com/codex/mcp) และ help ของ CLI บน Remote; ยังไม่ได้ทดสอบติดตั้งครบชุดด้วย Codex ในรอบนี้


Codex ใช้ไฟล์ `~/.codex/config.toml` (หรือ `$CODEX_HOME/config.toml`) วางส่วนนี้ต่อท้ายไฟล์แล้วตรวจด้วย `codex mcp list` (ค่าจริงบนเครื่องเรียนของผู้สอนต่างเล็กน้อย: `playwright` ใช้ `args = ["--cdp-endpoint", "http://127.0.0.1:9222"]` เพื่อต่อ headless Chrome ที่เปิดไว้แล้ว และ `excalidraw` มี `[mcp_servers.excalidraw.env]` กำหนด `EXPRESS_SERVER_URL = "http://127.0.0.1:8892"`, `EXCALIDRAW_NO_AUTOSTART = "1"`, `EXCALIDRAW_EXPORT_DIR = "/root/workspace/.mcp/excalidraw/diagrams"`)

```toml
[mcp_servers.excalidraw]
command = "mcp-excalidraw-server"

[mcp_servers.playwright]
command = "playwright-mcp"
args = ["--browser", "chromium"]

[mcp_servers.hello-lab]
command = "<PATH_TO_03_MCP>/labs/.venv/bin/python"
args = ["<PATH_TO_03_MCP>/labs/my-mcp-server/hello_server.py"]

[mcp_servers.kokoro-tts]
command = "<PATH_TO_03_MCP>/labs/.venv/bin/python"
args = ["<PATH_TO_03_MCP>/labs/my-mcp-server/tts_server.py"]

[mcp_servers.kokoro-tts.env]
KOKORO_DEVICE = "cpu"
```

ถ้าใช้ Codex เป็น Host ให้เริ่มจากคำขอภาษาธรรมดาในข้อ 4.2.2 ก่อน แล้วใช้คำสั่งด้านบนเป็นตัวเทียบผลเท่านั้น

#### 4.6.8 หมายเหตุสำหรับ Windows (แนวทาง — ยังไม่ได้ทดลอง)

- python ของ venv อยู่ที่ `labs\.venv\Scripts\python.exe` และใช้ `where mcp-excalidraw-server` แทน `command -v`
- ไม่ต้องรัน `install-deps` และไม่มี `espeak-ng` ผ่าน apt (Kokoro ยังอ่านคำทั่วไปได้ ถ้าต้องการ fallback ให้ติดตั้ง espeak-ng จาก https://github.com/espeak-ng/espeak-ng/releases)
- ใน `claude mcp add` ใช้ path เต็มแบบ Windows เช่น `C:\Users\<YOUR_USERNAME>\03_MCP\labs\.venv\Scripts\python.exe`
- `run.sh` เป็นสคริปต์ bash ให้รันผ่าน Git Bash/WSL หรือรันตรงจากโฟลเดอร์ `labs\kokoro-web`: `..\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8765`

#### 4.6.9 พรอมป์ต์ติดตั้งฉบับละเอียด (ฉบับเดิม — เก็บไว้เป็นข้อมูลอ้างอิง)

พรอมป์ต์สองบล็อกนี้คือฉบับที่ใช้ในการทดลองติดตั้งเมื่อ 19 กันยายน 2026 ซึ่งผู้สอนสั่งขั้นตอนให้ AI ครบทั้ง 9 ข้อ **ไม่ใช่เส้นทางการเรียนหลักแล้ว** (เส้นทางหลักคือข้อ 4.2 ส่งลิงก์ repo + คำขอสั้น ๆ) เก็บไว้เพราะหลักฐานใน `lab-results/setup-prompt/run-2026-09-19-072524/` เกิดจากพรอมป์ต์ชุดนี้ และใช้เทียบได้ว่าคำสั่งที่ AI ควรเลือกเองมีหน้าตาอย่างไร บล็อกนี้อ้างถึงโค้ดแล็บของบทเรียน (`labs/kokoro-web`, `labs/my-mcp-server`) จึงใช้ได้เฉพาะเมื่อมีโฟลเดอร์บทเรียนอยู่แล้ว

**ฉบับ Claude Code (เดิม)**

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

**ฉบับ Codex CLI (เดิม — ยังไม่ได้ทดสอบรันจริง)**

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

### 4.7 ข้อควรระวังที่พบจริง

1. ใช้ path แบบเต็ม (absolute) ใน `command`/`args` เพราะ Host เป็นคนเปิด process ไม่ใช่เรา และ working directory อาจไม่ใช่ที่เราคิด
2. server แบบ stdio ห้ามพิมพ์อะไรลง stdout นอกจาก JSON-RPC
3. MCP server ที่เพิ่งลงทะเบียนจะถูกโหลดตอนเริ่ม session ใหม่เท่านั้น จึงต้อง `/exit` แล้วเปิด `claude` ใหม่หลังรัน S0 (รวมถึงหลังที่ AI แก้ค่าใน `~/.claude.json` ให้)
4. `@playwright/mcp` รุ่นใหม่ใช้ Google Chrome เป็นค่าเริ่มต้น ถ้าติดตั้งแค่ chromium ต้องลงทะเบียนด้วย `--browser chromium` และถ้ารันเป็น root ต้องมี `--no-sandbox` (พบจริงในการทดสอบคอนเทนเนอร์ ข้อ 4.5)
5. Excalidraw MCP บนเครื่องเรียนเขียน/อ่านไฟล์ได้เฉพาะใน `EXCALIDRAW_EXPORT_DIR` (`/root/workspace/.mcp/excalidraw/diagrams`) ถ้าสั่ง export ไปที่อื่นจะได้ `Path traversal blocked` ต้องคัดลอกไฟล์ออกมาเอง (พบจริงใน Lab 5.4)
6. Playwright MCP บนเครื่องเรียนต่อกับ headless Chrome ตัวเดียวกับที่ Excalidraw ใช้แสดง canvas ถ้าแท็บของเว็บที่ทดสอบอยู่เบื้องหลัง การคลิกจะ timeout (พบจริงใน Lab 6 ดูวิธีแก้ในบทที่ 6.4)

---

<a id="ch5"></a>
## บทที่ 5 Case Study 1: Excalidraw MCP — ให้ AI วาดและแก้แผนภาพจาก Prompt

### 5.1 รู้จัก Excalidraw MCP

`mcp-excalidraw-server` เปิด canvas ในเบราว์เซอร์ (`http://127.0.0.1:8892`) และประกาศ tool ให้ AI สร้าง/แก้/ตรวจ/ส่งออกภาพ tool ที่ใช้บ่อย

| tool | ทำอะไร |
| --- | --- |
| `read_diagram_guide` | คู่มือสี ขนาด และ layout ที่ควรใช้ (AI ควรอ่านก่อนวาด) |
| `describe_scene` / `query_elements` / `get_element` | ดูว่าบน canvas มีอะไร (id, ตำแหน่ง, ข้อความ) |
| `batch_create_elements` / `create_element` | สร้างกล่อง ข้อความ ลูกศร (ลูกศรผูกกับกล่องด้วย `startElementId`/`endElementId`) |
| `update_element` / `delete_element` | แก้หรือลบทีละ element ตาม id |
| `set_viewport` / `get_canvas_screenshot` | จัดมุมมองแล้วถ่ายภาพ canvas กลับมาให้ AI ตรวจ |
| `export_to_image` / `export_scene` / `import_scene` | ส่งออก PNG/SVG, ส่งออก/นำเข้าไฟล์ `.excalidraw` |
| `create_from_mermaid` | แปลง Mermaid เป็น element บน canvas |

ก่อนเริ่ม: ถ้ายังไม่ได้ติดตั้ง ให้ส่งลิงก์ repo ต้นทาง <https://github.com/yctimlin/mcp_excalidraw> พร้อมคำขอตามข้อ 4.2 (หรือ S1 เฉพาะ Excalidraw ในข้อ 4.3.1) แล้วเปิด `claude` ใหม่ canvas จะเปิดอัตโนมัติที่ `http://127.0.0.1:3000` เมื่อ AI เรียก tool ครั้งแรก ถ้าเครื่องไม่มีจอ ให้ AI เปิดแท็บ canvas ผ่าน Playwright MCP ตามข้อ 2 ของ Prompt S5 (บนเครื่องเรียนของผู้สอน canvas อยู่ที่พอร์ต 8892 ในเบราว์เซอร์ headless)
![แผนภาพ Case Study 1: Prompt → Agent → MCP Client → Excalidraw MCP Server → Canvas พร้อมรายชื่อ tool ที่ใช้จริง](img/d05-case1-excalidraw-flow.png)

สิ่งที่ควรสังเกต: AI ไม่ได้ "วาดรูป" เอง แต่**ส่ง JSON ของ element** (ชนิด ตำแหน่ง ขนาด สี ข้อความ) ให้ server ทำงานกับ canvas จริง แล้วขอ screenshot กลับมาตรวจ ถ้าข้อความล้นกล่องหรือลูกศรทับกันก็สั่ง `update_element` แก้ วนจนผ่าน แล้วจึง export

### 5.2 Lab 5.1 — วาด Architecture Diagram

Prompt: [`labs/prompts/lab5-1-architecture-diagram.md`](labs/prompts/lab5-1-architecture-diagram.md)

```text
ใช้ Excalidraw MCP วาด Architecture Diagram ของ MCP บนเครื่องนี้ 1 ภาพ
โครงสร้างที่ต้องมี (ซ้ายไปขวา 3 โซน): Host (ผู้ใช้, LLM, MCP Client 3 ตัว) · MCP Server 3 ตัว · เครื่องมือจริง
ลูกศร: ผู้ใช้→LLM, LLM→Client, Client→Server (ป้าย JSON-RPC 1 เส้น), Server→เครื่องมือ
กติกา: อ่าน read_diagram_guide ก่อน · ห้ามใส่ text บนกล่องโซน · screenshot ตรวจแล้วแก้จนผ่าน · export PNG + .excalidraw
สุดท้ายรายงานลำดับ tool ที่เรียกทั้งหมด จำนวนรอบที่ต้องแก้ และปัญหาที่พบ
```

ผลจริง: ภาพ `img/d02-mcp-architecture.png` (บทที่ 2.1) การวาดรอบแรกพบว่าลูกศรจาก LLM ไป Client #2 และ #3 **ลากทะลุกล่อง Client #1** AI จึง `delete_element` ลูกศร 2 เส้น แล้ว `batch_create_elements` ลูกศรหักมุมอ้อมด้านซ้ายแทน ก่อน export (ดูแถวที่ 2 ใน [`trace.md`](lab-results/excalidraw/run-2026-09-19-062505/trace.md))

### 5.3 Lab 5.2 — วาด MCP Workflow

Prompt: [`labs/prompts/lab5-2-mcp-workflow.md`](labs/prompts/lab5-2-mcp-workflow.md) — ให้วาด sequence 5 คอลัมน์ 10 ข้อความ พร้อมกรอบ agent loop

ผลจริง: `img/d03-mcp-sequence.png` (บทที่ 2.2) ปัญหาที่พบ: ป้าย "วนซ้ำข้อ 4–9" วางทับลูกศรข้อ 9 แก้ด้วย `update_element` ย้ายป้าย 1 ครั้ง

### 5.4 Lab 5.3 — วาด Flow AI Agent → MCP Client → MCP Server → Tool

Prompt: [`labs/prompts/lab5-3-agent-client-server-tool-flow.md`](labs/prompts/lab5-3-agent-client-server-tool-flow.md)

ผลจริง: `img/d05-case1-excalidraw-flow.png` (ด้านบน) รอบแรกกล่องชื่อ tool กว้าง 140 px ทำให้ชื่อถูกตัดคำ (`describe_sce/ne`, `export_to_i/mage`) AI แก้ด้วย `update_element` 14 ครั้ง จัดใหม่เป็น 2 แถว กล่องกว้าง 280 px แล้วจึงผ่าน — บทเรียนคือ **screenshot ตรวจก่อน export เสมอ**

### 5.5 Lab 5.4 — ปรับแก้ Diagram จาก Prompt

Prompt: [`labs/prompts/lab5-4-modify-diagram.md`](labs/prompts/lab5-4-modify-diagram.md) สั่งให้เพิ่ม MCP Client #4 → `kokoro-tts` และเปลี่ยนสี server ที่นักศึกษาเขียนเองเป็นสีเขียว

| ก่อนแก้ | หลังแก้ตาม Prompt |
| --- | --- |
| ![ภาพก่อนแก้](lab-results/excalidraw/run-2026-09-19-062505/lab54-before.png) | ![ภาพหลังแก้: เพิ่มแถว kokoro-tts และเปลี่ยนสี server ที่เขียนเอง](lab-results/excalidraw/run-2026-09-19-062505/lab54-after.png) |

สิ่งที่เกิดขึ้นจริง (แถวที่ 9 ใน trace):

1. `import_scene` จากไฟล์ใน `img/` → error `Path traversal blocked: ... resolves outside the allowed directory "/root/workspace/.mcp/excalidraw/diagrams"` ต้อง import จากโฟลเดอร์ที่ server อนุญาต
2. import สำเร็จ 43 elements และแก้ต่อด้วย `update_element` ×5 + `batch_create_elements` แต่ screenshot พบว่า**กล่องกับข้อความเลื่อนไม่เท่ากัน** (กล่องเลื่อนขวา ราว 570 px ข้อความไม่เลื่อน)
3. AI ตัดสินใจ `clear_canvas` แล้วสร้างใหม่ทั้งภาพจาก JSON ต้นฉบับ + ส่วนที่ Prompt สั่งเพิ่ม (38 elements) → ผ่านและ export เป็น `img/d02b-mcp-architecture-modified.png`

บทเรียน: การ "แก้จาก Prompt" ทำได้จริง แต่ควรเก็บ JSON/ไฟล์ `.excalidraw` ต้นฉบับไว้ และเมื่อ tool ให้ผลผิดคาด ให้ตรวจด้วย screenshot แล้วเปลี่ยนวิธี ไม่ฝืนแก้ต่อ

### 5.6 หลักฐานและสิ่งที่เรียนรู้จาก Case Study 1

จาก [`trace.md`](lab-results/excalidraw/run-2026-09-19-062505/trace.md) (บันทึกทุก tool ที่เรียกในการวาด 9 ภาพ) และ [`run-info.json`](lab-results/excalidraw/run-2026-09-19-062505/run-info.json)

| ตัวเลขจากการทดลอง | ค่า |
| --- | --- |
| ภาพที่วาด | 9 (d01–d08 + d02b) |
| ภาพที่ผ่านรอบแรกโดยไม่ต้องแก้ | 2 (d01, d08) |
| ภาพที่ต้องแก้อย่างน้อย 1 รอบหลังดู screenshot | 7 |
| `batch_create_elements` / `update_element` / `delete_element` | 15 / 50 / 8 ครั้ง |
| `get_canvas_screenshot` | 18 ครั้ง |
| ปัญหาที่พบบ่อยที่สุด | ข้อความล้นกล่อง (กล่องแคบเกินสำหรับฟอนต์ลายมือ) รองลงมาคือลูกศรทับกล่อง/ป้ายทับลูกศร |

สิ่งที่นักศึกษาควรได้: (1) MCP ทำให้ AI ใช้เครื่องมือวาดภาพได้โดยไม่ต้องเขียน integration (2) คุณภาพงานมาจาก "วงจร วาด → ดู → แก้" ซึ่ง MCP รองรับผ่าน `get_canvas_screenshot` (3) Prompt ที่ดีต้องระบุ layout กติกา และวิธีตรวจ ไม่ใช่แค่ "วาดให้หน่อย"

### 5.7 เกณฑ์ตรวจ Lab 5

| เกณฑ์ | ผ่านเมื่อ |
| --- | --- |
| C1 ครบ 3 ภาพ + 1 ภาพแก้ | มี PNG และ `.excalidraw` ของ architecture, workflow, flow และภาพหลังแก้ (ก่อน/หลังต้องเทียบกันได้) |
| C2 อ่านได้ | ข้อความไม่ล้นกล่อง ลูกศรไม่ทับกล่อง (ตรวจจาก screenshot สุดท้าย) |
| C3 มีบันทึก tool | trace ระบุลำดับ tool ที่เรียก จำนวนรอบที่แก้ และ error ที่พบตามจริง |

---

<a id="ch6"></a>
## บทที่ 6 Case Study 2: Playwright MCP — ให้ AI ควบคุมเว็บ Kokoro TTS จริง

### 6.1 เว็บทดลอง Kokoro TTS Lab

เว็บอยู่ที่ [`labs/kokoro-web/`](labs/kokoro-web/) (FastAPI + หน้าเว็บเดียว) ใช้ [Kokoro-82M](https://github.com/hexgrad/kokoro) สังเคราะห์เสียงภาษาอังกฤษบน CPU มีองค์ประกอบครบตามโจทย์

| องค์ประกอบ | element | หมายเหตุ |
| --- | --- | --- |
| Text Input | `<textarea id="text">` ป้าย "ข้อความภาษาอังกฤษ" | Kokoro ยังไม่รองรับภาษาไทย จำกัด 500 ตัวอักษร |
| ตัวเลือกเสียง | `<select id="voice">` af_heart, af_bella, am_adam, am_michael | เสียงที่ทดสอบแล้วว่าโหลดได้ |
| Button | `<button id="speak-btn">Speak</button>` | ส่ง `POST /api/tts` |
| Result | `#status` + รายละเอียด ความยาวเสียง / เวลาที่ใช้สร้าง / sample rate / เสียง / ไฟล์ | ข้อความสำเร็จคือ "สร้างเสียงสำเร็จ" ข้อความผิดพลาดขึ้นต้นด้วย "เกิดข้อผิดพลาด" |
| Audio Player | `<audio id="player" controls>` | `src` ชี้ไปที่ `/audio/<file>.wav` |

เริ่มเว็บด้วยพรอมป์ต์: วางคำขอแล็บต่อเนื่อง S4 (ข้อ 4.3.4) AI จะสร้าง venv ติดตั้ง kokoro และรัน `labs/kokoro-web/run.sh` ให้ (เปิดที่ `http://127.0.0.1:8765` เก็บ pid ใน `server.pid`; ทำเองได้ด้วย `PYTHON=<python ของ venv> labs/kokoro-web/run.sh`) ตรวจ: `curl http://127.0.0.1:8765/api/health` → `{"ok":true,"device":"cpu","model_loaded":true,...}` ครั้งแรกที่กด Speak จะช้ากว่าปกติเพราะโหลดโมเดล (จาก curl: ครั้งแรก 6.66 วินาที ครั้งต่อไป 0.55 วินาที ตาม [`web-curl-tts-time.txt`](lab-results/own-server/run-2026-09-19-062712/web-curl-tts-time.txt) และ [`web-curl-tts-second.txt`](lab-results/own-server/run-2026-09-19-062712/web-curl-tts-second.txt))

![หน้าเว็บ Kokoro TTS Lab หลังเปิดครั้งแรก (screenshot จาก Playwright MCP)](lab-results/playwright/run-2026-09-19-064547/cs2-01-loaded.png)

### 6.2 Playwright MCP มองเห็นหน้าเว็บอย่างไร

`@playwright/mcp` ต่อกับ Chrome (บนเครื่องเรียนเป็น headless Chrome ผ่าน CDP พอร์ต 9222) และให้ AI "มองเห็น" หน้าเว็บผ่าน **accessibility snapshot** คือต้นไม้ของ element พร้อม role ชื่อ และ ref ไม่ใช่รูปภาพ ตัวอย่างจริงจาก [`snapshot-01-loaded.yml`](lab-results/playwright/run-2026-09-19-064547/snapshot-01-loaded.yml)

```yaml
- textbox "ข้อความภาษาอังกฤษ" [ref=e9]
- combobox "เสียงที่ใช้" [ref=e13]:
    - option "af_heart (หญิง อเมริกัน)" [selected]
    - option "am_adam (ชาย อเมริกัน)"
- button "Speak" [ref=e14] [cursor=pointer]
- paragraph [ref=e18]: ยังไม่ได้สร้างเสียง
- generic "เครื่องเล่นเสียงที่สร้างจาก Kokoro" [ref=e32]
```

AI ใช้ ref (เช่น `e14`) อ้างถึง element ในคำสั่งถัดไป ดังนั้น**เว็บที่ใส่ `<label>` และ `aria-label` ดีจะถูกควบคุมด้วย AI ได้แม่นกว่า** และประหยัดโทเคนกว่าการดูรูป

tool ที่ใช้ในแล็บนี้: `browser_navigate`, `browser_snapshot`, `browser_fill_form`, `browser_click`, `browser_wait_for`, `browser_take_screenshot`, `browser_evaluate`, `browser_console_messages`, `browser_network_requests`, `browser_tabs`

### 6.3 Lab 6.1–6.7 — Prompt ที่ให้นักศึกษาใช้

Prompt เต็ม: [`labs/prompts/lab6-playwright-kokoro.md`](labs/prompts/lab6-playwright-kokoro.md)

```text
ใช้ Playwright MCP ทำตามลำดับต่อไปนี้กับเว็บ http://127.0.0.1:8765/ และรายงานผลทุกขั้น
1. เปิดเว็บไซต์ และบอกชื่อหน้า
2. ทำ accessibility snapshot แล้วสรุปว่ามี element อะไรบ้าง พร้อม ref
3. กรอกข้อความ "Hello students. This audio was generated by Kokoro through a web form controlled by Playwright MCP." และเลือกเสียง am_adam
4. กดปุ่ม Speak
5. รอจนข้อความ "สร้างเสียงสำเร็จ" ปรากฏ แล้วอ่านค่า ความยาวเสียง เวลาที่ใช้สร้าง sample rate เสียง และ URL ไฟล์เสียง
6. ถ่าย screenshot ทั้งหน้า ชื่อ cs2-03-result.png
7. ใช้ screenshot และค่าที่อ่านได้เป็นหลักฐาน พร้อมตรวจ console และ network ว่า POST /api/tts ได้ 200 และไม่มี error
เพิ่มเติม: ล้าง textbox ให้ว่างแล้วกด Speak อีกครั้ง บันทึกข้อความผิดพลาดที่แสดง
กติกา: ถ้า tool ใดล้มเหลว ห้ามเดา ให้ใช้ browser_evaluate ตรวจสถานะหน้าเว็บหาสาเหตุ แก้ แล้วลองใหม่ และบันทึก error ตามจริง
```

**สิ่งที่ต้องแสดงให้เห็นในรายงานของนักศึกษา** คือสายงานทั้งเส้น

```text
Prompt (นักศึกษาพิมพ์ใน Claude Code)
↓
AI Agent (LLM ใน Claude Code อ่าน snapshot แล้วเลือก tool + argument)
↓
Playwright MCP Server (playwright-mcp รับ tools/call แล้วสั่ง Playwright)
↓
Browser (headless Chrome ผ่าน CDP :9222 เปิดเว็บ กรอกฟอร์ม คลิก)
↓
Web Application (Kokoro TTS Lab: Text Input → Button → POST /api/tts → Result → Audio Player)
↓
ผลลัพธ์ที่ตรวจได้ + Screenshot (หลักฐานของการทดลอง)
```

![Flow ของ Case Study 2 พร้อม tool ของ Playwright MCP ที่ใช้ในแต่ละขั้น](img/d06-case2-playwright-flow.png)

### 6.4 ผลการทดลองจริง (19 กันยายน 2026)

บันทึกเต็ม: [`trace.md`](lab-results/playwright/run-2026-09-19-064547/trace.md) · ข้อมูลรอบทดลอง: [`run-info.json`](lab-results/playwright/run-2026-09-19-064547/run-info.json)

| ขั้น | tool | ผลจริง |
| --- | --- | --- |
| 1 เปิดเว็บ | `browser_navigate` | title "Kokoro TTS Lab — ทดลอง Playwright MCP" · Console: 1 error (favicon 404 ไม่กระทบการทำงาน) |
| 2 ตรวจ element | `browser_snapshot` | เห็น textbox (e9), combobox (e13), button Speak (e14), ผลลัพธ์ (e18), เครื่องเล่นเสียง (e32) |
| 3 กรอกฟอร์ม | `browser_fill_form` | Playwright รัน `fill(...)` และ `selectOption('am_adam (ชาย อเมริกัน)')` |
| 4 กดปุ่ม (ครั้งที่ 1–2) | `browser_click` | **ล้มเหลว** `TimeoutError: browserBackend.callTool: Timeout 5000ms exceeded ... waiting for element to be visible, enabled and stable` |
| 4 วินิจฉัย | `browser_evaluate` | `document.visibilityState === "hidden"` ปุ่มอยู่ที่ (753, 386) ขนาด 220×47 `disabled: false` → แท็บอยู่เบื้องหลัง (Excalidraw MCP ใช้เบราว์เซอร์ตัวเดียวกันก่อนหน้า) แท็บที่ซ่อนไม่ render เฟรมใหม่ Playwright จึงรอ "stable" ไม่ผ่าน |
| 4 แก้ | `browser_tabs` select 0 → `browser_evaluate` | `visibilityState === "visible"` |
| 4 กดปุ่ม (ครั้งที่ 3) | `browser_click` | สำเร็จ `page.getByRole('button', { name: 'Speak' }).click()` |
| 5 ตรวจผล | `browser_wait_for` + `browser_snapshot` + `browser_evaluate` | "สร้างเสียงสำเร็จ" · ความยาวเสียง 7 วินาที · เวลาที่ใช้สร้าง 576 ms (cpu) · 24000 Hz · am_adam · `/audio/20260919-064750-65e6a515.wav` · `audio.duration = 7`, `readyState = 4` |
| 5 ตรวจ network / console | `browser_network_requests`, `browser_console_messages` | `[POST] /api/tts => [200] OK`, `[GET] /audio/....wav => [206] Partial Content` · console มีเพียง favicon 404 |
| 6 ถ่ายภาพ | `browser_take_screenshot` fullPage | `cs2-03-result.png` |
| 7 กรณีผิดพลาด | `browser_fill_form` (ว่าง) → `browser_click` → `browser_wait_for` | หน้าเว็บแสดง `เกิดข้อผิดพลาด: กรุณาพิมพ์ข้อความก่อน` (`cs2-04-error-empty.png`) |

![หลังกรอกข้อความและเลือกเสียง am_adam](lab-results/playwright/run-2026-09-19-064547/cs2-02-filled.png)

![หลังกด Speak: สร้างเสียงสำเร็จ 7 วินาที 576 ms และเครื่องเล่นเสียงพร้อมเล่น](lab-results/playwright/run-2026-09-19-064547/cs2-03-result.png)

![กรณีข้อความว่าง: เกิดข้อผิดพลาด กรุณาพิมพ์ข้อความก่อน](lab-results/playwright/run-2026-09-19-064547/cs2-04-error-empty.png)

ไฟล์เสียงที่เว็บสร้างในรอบนี้: [`result-audio.wav`](lab-results/playwright/run-2026-09-19-064547/result-audio.wav) (24000 Hz, 7.0 วินาที ตรวจด้วย soundfile) · snapshot หลังสำเร็จ: [`snapshot-03-result.yml`](lab-results/playwright/run-2026-09-19-064547/snapshot-03-result.yml) · console: [`console.log`](lab-results/playwright/run-2026-09-19-064547/console.log)

### 6.5 สิ่งที่เรียนรู้จาก Case Study 2

1. **ใช้ screenshot เป็นหลักฐาน แต่ตัดสินด้วยข้อมูล** — ค่าที่อ่านจาก snapshot/`browser_evaluate` (7 วินาที, 576 ms, HTTP 200) ตรวจซ้ำได้ ส่วน screenshot ยืนยันว่าผู้ใช้เห็นแบบเดียวกัน
2. **error ของ tool ไม่ได้แปลว่าเว็บพัง** — click timeout 2 ครั้งเกิดจากแท็บอยู่เบื้องหลัง วิธีที่ถูกคือใช้ tool วินิจฉัย (`browser_evaluate`) หาสาเหตุ ไม่ใช่สุ่มลองใหม่หรือเดาว่าเว็บมีบั๊ก
3. **ข้อจำกัดของเครื่องมือมีจริง** — screenshot ที่สั่งด้วยชื่อไฟล์แบบ relative ถูกบันทึกที่ working directory ของ process `playwright-mcp` ไม่ใช่ `--output-dir` ต้องย้ายเข้าโฟลเดอร์หลักฐานเอง (บันทึกไว้ใน trace)
4. งานเดียวกันนี้ทำผ่าน MCP tool `speak` ได้โดยไม่ต้องเปิดเบราว์เซอร์ (บทที่ 7.5) — Playwright MCP เหมาะกับการ**ทดสอบเว็บที่มีอยู่แล้ว** ส่วน MCP server ของเราเองเหมาะกับการ**ให้ AI เรียกความสามารถโดยตรง**

### 6.6 เกณฑ์ตรวจ Lab 6

| เกณฑ์ | ผ่านเมื่อ |
| --- | --- |
| C1 ครบ 7 ขั้น | มีหลักฐานของ เปิดเว็บ / snapshot / กรอกฟอร์ม / คลิก / ตรวจผล / screenshot / สรุปโดยอ้าง screenshot |
| C2 ผลตรวจได้ | รายงานระบุความยาวเสียง เวลาที่ใช้ และสถานะ HTTP ของ `POST /api/tts` จาก tool จริง ไม่ใช่จากการเดา |
| C3 จัดการความผิดพลาด | ถ้ามี tool ล้มเหลว ต้องบันทึกข้อความ error ตามจริงและวิธีหาสาเหตุ; ทดสอบกรณีข้อความว่างและบันทึกข้อความผิดพลาดของเว็บ |

---

<a id="ch7"></a>
## บทที่ 7 สร้าง MCP Server ของตัวเองด้วย Python

![สถาปัตยกรรม MCP server ที่นักศึกษาสร้างเอง และวิธีทดสอบ 3 ทาง](img/d07-own-server.png)

### 7.1 ติดตั้งและโครงสร้างไฟล์

ถ้าทำคำขอแล็บต่อเนื่อง S4 (ข้อ 4.3.4) แล้ว venv `labs/.venv` จะมี `mcp[cli]` และ server ทั้งสองถูกตั้งค่าไว้แล้ว ถ้าจะทำเอง:

```bash
python3 -m venv labs/.venv && labs/.venv/bin/pip install "mcp[cli]"   # Python SDK 2.0 (มี mcp dev / mcp run ด้วย)
cd labs/my-mcp-server && cat README-run.md                              # คำสั่งทั้งหมดของแล็บนี้
```

| ไฟล์ใน [`labs/my-mcp-server/`](labs/my-mcp-server/) | หน้าที่ |
| --- | --- |
| `hello_server.py` | MCP server ตัวแรก: 3 tools, 1 resource, 1 prompt รันได้ทั้ง stdio และ `--http` |
| `tts_server.py` | MCP server ตัวที่สอง: ห่อ Kokoro (`speak`, `list_voices`) |
| `client_test.py` | MCP client ทดสอบโดยไม่ใช้ LLM (`--server hello|tts|http`, `--wire` บันทึกสาย) |
| `wire_capture.py` | proxy stdio ดักทุกบรรทัด JSON-RPC ลง `.jsonl` |
| `mcp.json`, `codex-config-snippet.toml` | ตั้งค่าให้ Claude Code / Codex รู้จัก server |
| `claude_lab.sh`, `summarize_stream.py` | รัน `claude -p` แล้วสรุป tool ที่ถูกเรียกเป็น Markdown |

### 7.2 Lab 7.1 — เขียน `hello_server.py`

โค้ดเต็ม: [`labs/my-mcp-server/hello_server.py`](labs/my-mcp-server/hello_server.py) ส่วนสำคัญ

```python
from mcp.server import MCPServer

mcp = MCPServer("hello-lab", instructions="MCP server สำหรับแล็บ 03_MCP: เครื่องมือคำนวณและนับคำอย่างง่าย")

@mcp.tool()
def add(a: int, b: int) -> int:
    """บวกเลขจำนวนเต็มสองจำนวน / Add two integers and return the sum."""
    return a + b

@mcp.tool()
def count_words(text: str) -> dict:
    """นับจำนวนคำและตัวอักษรในข้อความ / Count words and characters in a text."""
    words = text.split()
    return {"words": len(words), "characters": len(text), "longest_word": max(words, key=len) if words else ""}

@mcp.resource("lab://info")
def lab_info() -> str:
    """ข้อมูลของแล็บนี้ (resource = ข้อมูลให้อ่าน ไม่ใช่การกระทำ)"""
    return "hello-lab: MCP server ตัวอย่างของบทเรียน 03_MCP (KMITL). ..."

@mcp.prompt()
def explain_mcp(topic: str) -> str:
    """แม่แบบข้อความขอให้อธิบายหัวข้อเกี่ยวกับ MCP แบบเข้าใจง่าย"""
    return f"อธิบายเรื่อง '{topic}' ในบริบทของ Model Context Protocol ให้นักศึกษาปีหนึ่งเข้าใจ ..."

if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8766)
    else:
        mcp.run()  # stdio: อ่าน JSON-RPC จาก stdin เขียนคำตอบลง stdout (ห้าม print() ลง stdout!)
```

สิ่งที่**ไม่ต้องเขียน**: JSON Schema (type hint `a: int, b: int` กลายเป็น `inputSchema`), การ parse JSON-RPC, การจัดการ transport และเวอร์ชันโปรโตคอล — SDK ทำให้ทั้งหมด docstring กลายเป็น `description` ที่ LLM อ่านเพื่อตัดสินใจเลือก tool จึงควรเขียนให้ชัด

งานของนักศึกษา: เพิ่ม tool ของตัวเองอย่างน้อย 1 ตัว (เช่น `to_upper(text)` หรือ `bmi(weight_kg, height_m)`) แล้วทำ Lab 7.2–7.3 ให้เห็นว่า LLM เรียกได้

### 7.3 Lab 7.2 — ทดสอบด้วย Python client และดูข้อความจริงบนสาย

```bash
cd labs/my-mcp-server
/opt/venv/bin/python client_test.py --server hello --wire wire-hello.jsonl
```

`client_test.py` ทำหน้าที่เหมือน MCP Client ใน Host: เชื่อมต่อ → `list_tools` / `list_resources` / `list_prompts` → `call_tool` / `read_resource` / `get_prompt` (ใช้ `from mcp import Client` และ `stdio_client(StdioServerParameters(command=..., args=[...]))`)

ผลจริง ([`client-hello-output.txt`](lab-results/own-server/run-2026-09-19-062712/client-hello-output.txt))

```text
== connected ==
protocol_version: 2026-07-28
server_info: {"name": "hello-lab", "version": ""}
server_capabilities: {"prompts": {"listChanged": true}, "resources": {"subscribe": true, "listChanged": true}, "tools": {"listChanged": true}}
== tools/list ==
{"name": "add", "description": "บวกเลขจำนวนเต็มสองจำนวน / Add two integers and return the sum.",
 "inputSchema": {"type": "object", "properties": {"a": {"title": "A", "type": "integer"}, "b": {"title": "B", "type": "integer"}}, "required": ["a", "b"]}}
...
== tools/call add(17, 25) ==   → content: [{"type": "text", "text": "42"}], structuredContent: {"result": 42}
== tools/call count_words(...) ==  → {"words": 9, "characters": 56, "longest_word": "Protocol"}
```

ข้อความบนสาย ([`wire-hello.jsonl`](lab-results/own-server/run-2026-09-19-062712/wire-hello.jsonl) 18 บรรทัด): ข้อความแรกคือ `server/discover` (client แบบ 2026-07-28 ไม่ส่ง `initialize`) ตามด้วย `tools/list`, `resources/list`, `prompts/list`, `tools/call` ×3, `resources/read`, `prompts/get` ทุก request แนบ `_meta.io.modelcontextprotocol/protocolVersion: "2026-07-28"` ดูตัวอย่างข้อความเต็มในบทที่ 2.2

### 7.4 Lab 7.3 — ให้ Claude Code ค้นพบและเรียก tool ของเรา

**หมายเหตุ** — ถ้าตั้งค่า server ด้วย S4 (ข้อ 4.3.4) แล้ว นักศึกษาวาง Prompt เหล่านี้ใน `claude` ได้ทันทีโดยไม่ต้องใส่ `--mcp-config` Prompt และผลอยู่ใน [`labs/prompts/lab7-own-mcp-server.md`](labs/prompts/lab7-own-mcp-server.md) และ `lab-results/own-server/run-2026-09-19-062712/`

| รอบ | Prompt (ย่อ) | สิ่งที่ Claude ทำจริง | หลักฐาน |
| --- | --- | --- | --- |
| discover | แสดงรายชื่อ tool จาก hello-lab และ kokoro-tts พร้อมพารามิเตอร์ ไม่ต้องเรียก | system/init รายงาน server ทั้งสอง `connected`; Claude ใช้ `ToolSearch` โหลด schema ของ `mcp__hello-lab__add`, `count_words`, `get_time`, `mcp__kokoro-tts__list_voices`, `speak` แล้วตอบรายการพร้อมชนิดพารามิเตอร์ ไม่เรียก tool (7.1 วินาที) | [`claude-discover-summary.md`](lab-results/own-server/run-2026-09-19-062712/claude-discover-summary.md) |
| use | บวก 17 กับ 25, บอกเวลา, นับคำในประโยค, อ่าน resource lab://info แล้วสรุปว่าเรียกอะไรบ้าง | `mcp__hello-lab__add {"a":17,"b":25}` → 42 · `get_time` → `2026-09-19T06:30:20Z` · `count_words` → 9 คำ 56 ตัวอักษร · `ReadMcpResourceTool {"server":"hello-lab","uri":"lab://info"}` (6 turn, 9.7 วินาที) | [`claude-use-summary.md`](lab-results/own-server/run-2026-09-19-062712/claude-use-summary.md), [`claude-use-stream.jsonl`](lab-results/own-server/run-2026-09-19-062712/claude-use-stream.jsonl) |
| tts | ใช้ tool speak สร้างเสียงจากประโยคที่กำหนด แล้วบอก path และความยาว | `mcp__kokoro-tts__speak {"text": "Model Context Protocol lets one server serve many agents."}` → ไฟล์ `.wav` ยาว 4.45 วินาที gen 684 ms (13.7 วินาที) | [`claude-tts-summary.md`](lab-results/own-server/run-2026-09-19-062712/claude-tts-summary.md) |

บนสาย ([`claude-use-wire-hello.jsonl`](lab-results/own-server/run-2026-09-19-062712/claude-use-wire-hello.jsonl)) Claude Code 2.1.258 เริ่มด้วย

```json
{"method": "initialize", "params": {"protocolVersion": "2025-11-25",
  "capabilities": {"roots": {"listChanged": true}, "elicitation": {}},
  "clientInfo": {"name": "claude-code", "title": "Claude Code", "version": "2.1.258"}}, "jsonrpc": "2.0", "id": 0}
```

แล้วส่ง `notifications/initialized`, `tools/list`, `prompts/list`, `resources/list` และเมื่อ LLM เลือก tool จึงส่ง `tools/call` (มี `_meta.claudecode/toolUseId` แนบมาด้วย) — เป็นภาพเดียวกับแผนภาพลำดับในบทที่ 2.2 แต่เป็นของจริง

### 7.5 Lab 7.4 — เปิด Kokoro เป็น MCP tool (`tts_server.py`)

โค้ดอยู่ในบทที่ 3 (แบบที่ 3) ทดสอบด้วย `client_test.py --server tts --wire wire-tts.jsonl` ได้ไฟล์เสียง 4.45 วินาที gen 693 ms ([`client-tts-output.txt`](lab-results/own-server/run-2026-09-19-062712/client-tts-output.txt), [`speak-output.wav`](lab-results/own-server/run-2026-09-19-062712/speak-output.wav)) และ Claude Code เรียกได้ตามตารางด้านบน

เปรียบเทียบกับ Lab 6: งานเดียวกัน (สังเคราะห์เสียง) แต่ผ่าน MCP tool AI ไม่ต้องเปิดเบราว์เซอร์ ไม่ต้องรู้ URL และผลกลับมาเป็น JSON ที่ตรวจได้ทันที นี่คือความหมายของ "MCP เป็นตัวกลางที่ทำให้ AI ใช้ tool ภายนอกได้โดยไม่ต้องเขียน integration ใหม่ทุกครั้ง"

### 7.6 Streamable HTTP: server เดิม เปิดเป็นบริการผ่านเครือข่าย

```bash
/opt/venv/bin/python hello_server.py --http            # เทอร์มินัล 1: http://127.0.0.1:8766/mcp
/opt/venv/bin/python client_test.py --server http      # เทอร์มินัล 2: Client("http://127.0.0.1:8766/mcp")
```

ผ่านครบเหมือน stdio ([`client-http-output.txt`](lab-results/own-server/run-2026-09-19-062712/client-http-output.txt)) เมื่อลองยิงด้วย curl ตรง ๆ ([`http-curl.txt`](lab-results/own-server/run-2026-09-19-062712/http-curl.txt)) จะเห็นว่า transport นี้มีกติกาเพิ่ม: ไม่ใส่ header พิเศษได้ `400 Bad Request: Missing session ID`; ใส่ `mcp-session-id` ที่ server แจกได้ `-32602 Invalid request parameters` (เข้าโหมด session แบบเก่า); ต้องใส่ `MCP-Protocol-Version: 2026-07-28` พร้อม `Mcp-Method: <method>` (และ `Mcp-Name: add` สำหรับ `tools/call`) จึงได้ 200 ทั้ง `server/discover`, `tools/list`, `tools/call` (ผล 42) โดยไม่ต้องมี session — บทเรียนคือ**ใช้ SDK client เถอะ** แต่รู้ไว้ว่าข้างล่างเป็น HTTP ธรรมดา

### 7.7 ข้อผิดพลาดที่พบระหว่างทำแล็บ (จาก [`trace.md`](lab-results/own-server/run-2026-09-19-062712/trace.md))

| ปัญหา | สาเหตุ | วิธีแก้ |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'mcp.server.fastmcp'` | SDK 2.0 เปลี่ยน API จาก `FastMCP` เป็น `MCPServer` (`from mcp.server import MCPServer`) | ใช้ API ใหม่ ตรวจ `pip show mcp` ก่อนเขียน |
| GPU: `RuntimeError: GET was unable to find an engine to execute this computation` | cuDNN กับ torch nightly บน RTX 5090 | ใช้ CPU (ค่าเริ่มต้น) หรือ `torch.backends.cudnn.enabled = False` ก่อนสร้าง pipeline |
| `pkill -f 'hello_server.py --http'` ฆ่า shell ของตัวเอง (exit 144) | pattern ตรงกับคำสั่ง shell ที่กำลังรัน | เก็บ pid แล้ว `kill <pid>` |
| curl ยิง Streamable HTTP ได้ 400 / -32602 | ไม่ได้ใส่ header ตามสเปก 2026-07-28 | ใส่ `MCP-Protocol-Version` และ `Mcp-Method` (ดู 7.6) |

### 7.8 เกณฑ์ตรวจ Lab 7

| เกณฑ์ | ผ่านเมื่อ |
| --- | --- |
| C1 server ทำงาน | `client_test.py` เห็น tool ที่เพิ่มเองใน `tools/list` และเรียกได้ผลถูกต้อง |
| C2 มี wire log | `wire-*.jsonl` แสดง `tools/list` และ `tools/call` ของ tool ที่เพิ่มเอง พร้อมระบุเวอร์ชันโปรโตคอลที่เห็น |
| C3 LLM เรียกได้จริง | `claude -p --mcp-config` แล้ว stream-json แสดง `mcp__<server>__<tool>` ถูกเรียกพร้อม argument และผล |

---

<a id="ch8"></a>
## บทที่ 8 สรุป แบบฝึกหัด และเกณฑ์ตรวจงานส่ง

### 8.1 สรุปสิ่งที่ต้องตอบได้

1. **MCP คืออะไร** — โปรโตคอลเปิด (JSON-RPC 2.0) ให้แอป AI ค้นพบและเรียกใช้เครื่องมือ/ข้อมูลภายนอกผ่านมาตรฐานเดียว
2. **แก้ปัญหาอะไร** — ตัวเชื่อม N×M ระหว่างแอป AI กับเครื่องมือ กลายเป็น N+M
3. **ทำไม Agent ต้องใช้** — LLM ทำอะไรกับโลกภายนอกเองไม่ได้ MCP ให้ tool ถูกค้นพบ (`tools/list`) และเรียก (`tools/call`) แบบมาตรฐาน พร้อมจุดขออนุมัติผู้ใช้
4. **โครงสร้าง** — Host (มี LLM + MCP Client 1 ตัวต่อ 1 server) ↔ MCP Server (Tools / Resources / Prompts) ↔ เครื่องมือจริง; transport stdio หรือ Streamable HTTP
5. **ต่างจาก function/API** — function เรียกได้ใน process เดียว, API เรียกได้ทุกที่แต่ LLM ไม่รู้จักเอง, MCP ให้ LLM รู้จักและเรียกได้เองพร้อม schema และการอนุมัติ
6. **ใช้ MCP ที่มีอยู่** — Excalidraw MCP วาด/แก้ภาพจาก Prompt ได้จริง (9 ภาพ), Playwright MCP ควบคุมเว็บได้จริง (กรอก คลิก ตรวจ screenshot)
7. **สร้างเอง** — `MCPServer` + `@mcp.tool()` ไม่กี่บรรทัด ทดสอบได้ 3 ทาง (Python client, Claude Code, HTTP) และเห็นข้อความจริงบนสายด้วย `wire_capture.py`
8. **หลักฐาน** — ทุกผลต้องย้อนไปหาไฟล์ใน `lab-results/` ได้ และ error ที่พบต้องบันทึกตามจริง

### 8.2 แบบฝึกหัดต่อยอด

1. เพิ่ม tool `read_csv_summary(path)` ใน `hello_server.py` ที่คืนจำนวนแถวและชื่อคอลัมน์ แล้วให้ Claude Code สรุปไฟล์ CSV ผ่าน tool นี้ (ระวังเรื่องความปลอดภัยของ path)
2. เพิ่ม resource `lab://voices` ใน `tts_server.py` และดูว่า Claude Code อ่านผ่าน `ReadMcpResourceTool` ได้ไหม
3. ใช้ Playwright MCP ทดสอบเว็บ Mock-up จองห้องประชุมจากบทที่ 02 ครบ 5 ฟีเจอร์ แล้วเทียบกับที่เคยใช้ Python Playwright ตรง ๆ ว่าต่างกันอย่างไร
4. ใช้ Excalidraw MCP วาดสถาปัตยกรรมของโปรเจกต์ตัวเอง แล้วสั่งแก้ 2 รอบด้วย Prompt เก็บภาพก่อน/หลัง
5. (ท้าทาย) รัน `hello_server.py --http` แล้วตั้งค่าให้ Claude Code ต่อผ่าน URL แทน stdio (`claude mcp add --transport http ...`) แล้วเทียบ wire log — **แนวทาง ยังไม่ได้ทดลองในบทเรียนนี้**

### 8.3 เกณฑ์ตรวจงานส่งรวม

| ส่วน | น้ำหนัก | ผ่านเมื่อ |
| --- | --- | --- |
| Lab 5 Excalidraw MCP | 25% | C1–C3 ในบทที่ 5.7 |
| Lab 6 Playwright MCP | 25% | C1–C3 ในบทที่ 6.6 |
| Lab 7 MCP server ของตัวเอง | 35% | C1–C3 ในบทที่ 7.8 |
| รายงานสั้น | 15% | อธิบาย N×M → N+M ด้วยตัวอย่างของตัวเอง, ระบุความต่างจาก API, และอ้างไฟล์หลักฐานของตัวเองอย่างน้อย 3 ไฟล์ |

ทุกส่วนหักคะแนนเมื่อ: อ้างตัวเลขที่ไม่มีไฟล์รองรับ, ไม่บันทึก error ที่เกิดจริง, หรือใช้ภาพที่ไม่ได้สร้างผ่าน MCP

### 8.4 อภิธานศัพท์

| คำ | ความหมายแบบสั้น |
| --- | --- |
| MCP (Model Context Protocol) | โปรโตคอลเปิดให้แอป AI ต่อกับเครื่องมือ/ข้อมูลภายนอก |
| Host | โปรแกรม AI ที่ผู้ใช้ใช้ เช่น Claude Code, Codex; เป็นเจ้าของ LLM และ MCP Client |
| MCP Client | ตัวเชื่อมใน Host ที่คุยกับ MCP Server 1 ตัว |
| MCP Server | โปรแกรมที่ประกาศ Tools / Resources / Prompts และทำงานจริง |
| Tool | ฟังก์ชันที่ LLM เรียกได้ (model-controlled) มี `inputSchema` |
| Resource | ข้อมูลที่อ่านได้ผ่าน URI เช่น `lab://info` |
| Prompt | แม่แบบข้อความที่ server เตรียมไว้ให้ผู้ใช้/โมเดล |
| JSON-RPC 2.0 | รูปแบบข้อความ `{jsonrpc, id, method, params}` / `{jsonrpc, id, result}` ที่ MCP ใช้ |
| `tools/list`, `tools/call` | คำขอ "มี tool อะไรบ้าง" และ "เรียก tool นี้ด้วย argument นี้" |
| Transport | วิธีส่งข้อความ: stdio (subprocess) หรือ Streamable HTTP (POST + SSE) |
| stdio | ส่ง JSON-RPC ทีละบรรทัดผ่าน stdin/stdout ของ subprocess |
| Streamable HTTP | ส่งผ่าน HTTP endpoint เดียว ตอบเป็น JSON หรือ SSE stream |
| `inputSchema` | JSON Schema ของ argument ที่ tool รับ (SDK สร้างจาก type hint) |
| accessibility snapshot | ต้นไม้ element ของหน้าเว็บที่ Playwright MCP ให้ AI "มองเห็น" |
| wire log | บันทึกข้อความ JSON-RPC ทุกบรรทัดที่วิ่งระหว่าง client กับ server |

### 8.5 อ้างอิง

- สเปก MCP รุ่น 2026-07-28: https://modelcontextprotocol.io/specification/2026-07-28 (Architecture, Transports, Server features → Tools)
- Python SDK: https://py.sdk.modelcontextprotocol.io/ (แพ็กเกจ `mcp` 2.0.0)
- Playwright MCP: https://github.com/microsoft/playwright-mcp (`@playwright/mcp` 0.0.80)
- Excalidraw MCP: แพ็กเกจ `mcp-excalidraw-server` 2.0.0 (npm)
- Kokoro TTS: https://github.com/hexgrad/kokoro (`kokoro` 0.9.4, โมเดล Kokoro-82M)
- เอกสาร Claude Code เรื่อง MCP: `claude mcp --help`

---

<a id="appendix"></a>
## ภาคผนวก: ดัชนีไฟล์หลักฐาน

| โฟลเดอร์ | ไฟล์สำคัญ |
| --- | --- |
| `lab-results/excalidraw/run-2026-09-19-062505/` | `trace.md` (ทุก tool ที่เรียกตอนวาด 9 ภาพ + ข้อค้นพบ), `lab54-before.png`, `lab54-after.png`, `run-info.json`, `sha256.txt` |
| `lab-results/playwright/run-2026-09-19-064547/` | `trace.md`, `cs2-01-loaded.png`, `cs2-02-filled.png`, `cs2-03-result.png`, `cs2-04-error-empty.png`, `snapshot-*.yml`, `console.log`, `result-audio.wav`, `run-info.json`, `sha256.txt` |
| `lab-results/own-server/run-2026-09-19-062712/` | `trace.md`, `run-info.json`, `wire-hello.jsonl`, `wire-tts.jsonl`, `client-hello-output.txt`, `client-tts-output.txt`, `client-http-output.txt`, `http-curl.txt`, `http-server.log`, `claude-{discover,use,tts}-{prompt.txt,stream.jsonl,summary.md,wire-hello.jsonl,wire-tts.jsonl}`, `web-curl-*.json/txt`, `web-wav-check.txt`, `speak-output.wav`, `sha256.json` |
| `img/` | `d01`–`d08` และ `d02b` ทั้ง `.png` และ `.excalidraw` |
| `lab-results/setup-prompt/run-*/` | ผลการรันพรอมป์ต์ติดตั้งฉบับละเอียด (ข้อ 4.6.9) และ S5 ในคอนเทนเนอร์เปล่า (stream-json, `setup-report.md`, `claude mcp list`, เวอร์ชัน, error จริง) |
| `labs/` | โค้ดแล็บและพรอมป์ต์ของบทเรียน (`prompts/setup-00..06-*.md` = คำขอติดตั้ง/ตรวจ/ถอน) |

**วิธีรันซ้ำทั้งบทเรียน**: (1) `claude` แล้วส่งคำขอพร้อมลิงก์ repo ตามข้อ 4.2.1 (2) `/exit` แล้วเปิด `claude` ใหม่ วาง Prompt S5 เพื่อยืนยันว่าเรียก tool ได้จริง (3) ทำ S4 (ข้อ 4.3.4) เมื่อต้องใช้โค้ดแล็บของบทเรียน แล้วใช้ Prompt ใน `labs/prompts/` ทีละแล็บ (4) สำหรับบทที่ 7 ทำตาม `labs/my-mcp-server/README-run.md` (5) จบบทเรียนแล้วใช้ Prompt S6 ถอนการตั้งค่า

*บทเรียนนี้ออกแบบและสร้างหลักฐานโดย Claude Fable 5.1 ผ่าน Claude Code 2.1.258 เมื่อ 19 กันยายน 2026 (สเปกการออกแบบ: `labs/design-spec.md`) — โค้ดเว็บและ MCP server ของนักศึกษาเขียนใน session เดียวกัน ไม่ได้ใช้ Codex ในรอบนี้*
