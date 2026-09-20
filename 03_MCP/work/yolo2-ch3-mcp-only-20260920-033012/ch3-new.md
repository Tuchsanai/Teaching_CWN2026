<a id="ch3"></a>
## บทที่ 3 สร้าง Kokoro เป็น MCP tool ด้วย `MCPServer` และเรียกใช้ผ่าน Host

ใช้งานเดียวกันตลอดบทเรียน: **สังเคราะห์เสียงภาษาอังกฤษด้วย Kokoro-82M** บทนี้ตอบสองคำถาม: เขียน MCP server ที่เปิด Kokoro เป็น tool อย่างไร และ Host เรียก tool นั้นอย่างไร โค้ดจริงอยู่ที่ [`labs/my-mcp-server/tts_server.py`](labs/my-mcp-server/tts_server.py) ด้านล่างคือฉบับย่อที่ตัดเฉพาะ docstring ออก ยังครบทุก `import` และการเริ่ม server

**สิ่งที่โค้ดนี้พึ่งพา (ติดตั้งในบทที่ 4)** — server ไม่ได้สังเคราะห์เสียงเอง แต่เรียก `kokoro_core.synthesize()` จากโฟลเดอร์เว็บของบทเรียน [`labs/kokoro-web/kokoro_core.py`](labs/kokoro-web/kokoro_core.py) จึงต้องมีโฟลเดอร์ `labs/` ครบตามโครงสร้างเดิม และต้องติดตั้งแพ็กเกจ `mcp[cli]` (Python SDK 2.0), `kokoro`, `soundfile`, `torch` ไว้ใน venv ก่อน (คำขอ S4 ข้อ 4.3.4 หรือคำสั่งทำเองข้อ 4.6) บทนี้อ่านโค้ดอย่างเดียว ยังไม่ต้องรัน

```python
# tts_server.py (ฉบับย่อ) — เปิด Kokoro TTS เป็น MCP tool ผ่าน stdio
import pathlib
import sys

# ให้ import kokoro_core จากโฟลเดอร์ labs/kokoro-web ได้ โดยไม่ต้องคัดลอกโค้ด
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "kokoro-web"))
import kokoro_core

from mcp.server import MCPServer

mcp = MCPServer(
    "kokoro-tts",
    instructions="แปลงข้อความภาษาอังกฤษเป็นไฟล์เสียง .wav ด้วย Kokoro-82M (ไม่รองรับภาษาไทย)",
)


@mcp.tool()
def list_voices() -> list[str]:
    """รายชื่อเสียงที่ใช้ได้ / Available Kokoro voices."""
    return kokoro_core.VOICES


@mcp.tool()
def speak(text: str, voice: str = "af_heart") -> dict:
    """สังเคราะห์เสียงภาษาอังกฤษจากข้อความ แล้วคืน path ของไฟล์ .wav พร้อมความยาว (วินาที)"""
    r = kokoro_core.synthesize(text, voice)
    return {"path": r["path"], "duration_sec": r["duration_sec"],
            "sample_rate": r["sample_rate"], "gen_ms": r["gen_ms"], "voice": r["voice"]}


if __name__ == "__main__":
    mcp.run()
```

อ่านทีละส่วน (ตรงกับแพ็กเกจ `mcp` 2.0.0 ที่อยู่บนเครื่องเรียน ตรวจได้ด้วย `python -c "from mcp.server import MCPServer"`):

| ส่วน | ทำอะไร |
| --- | --- |
| `from mcp.server import MCPServer` | คลาส server ระดับสูงของ SDK 2.0 ชื่อนี้ตรงตามแพ็กเกจที่ติดตั้ง (บทเรียนนี้ไม่ใช้ชื่อ `FastMCP` ของ SDK รุ่นก่อน) ส่วน `sys.path.insert(...)` สองบรรทัดก่อนหน้าทำให้ `import kokoro_core` หาไฟล์ในโฟลเดอร์ข้างเคียงเจอ |
| `MCPServer("kokoro-tts", instructions=...)` | สร้าง server 1 ตัว อาร์กิวเมนต์แรกคือชื่อที่ Host เห็นใน `serverInfo.name` (Claude Code นำไปตั้งชื่อ tool ว่า `mcp__kokoro-tts__speak`) ส่วน `instructions` ถูกส่งกลับในผลของ `initialize` ให้โมเดลอ่านว่า server นี้ใช้ทำอะไร |
| `@mcp.tool()` | ลงทะเบียนฟังก์ชัน Python ธรรมดาเป็น tool: ชื่อฟังก์ชันเป็นชื่อ tool, docstring เป็น `description`, type hint กลายเป็น `inputSchema` (จึงได้ `text` เป็นฟิลด์บังคับ และ `voice` มี `default: "af_heart"`) ค่าที่ `return` ถูกแปลงเป็น JSON ใส่ใน `content[0].text` ของผล `tools/call` |
| `mcp.run()` | เริ่ม server และรอรับข้อความ JSON-RPC ค่าเริ่มต้นคือ transport `stdio` (อ่านจาก stdin เขียนลง stdout) จึงเหมาะกับ Host ที่เปิด server เป็น subprocess เอง ถ้าจะเปิดผ่านเครือข่ายใช้ `mcp.run(transport="streamable-http")` (บทที่ 7.6) |

ข้อสังเกตสำคัญ: `kokoro_core` ถูกเรียก **ภายใน** server เท่านั้น โมเดลไม่เห็นโค้ด Python และไม่ได้ `import` อะไร มันเห็นแค่ชื่อ tool, `description` และ `inputSchema` ที่ server ประกาศออกมา นี่คือสิ่งที่ทำให้ server ตัวเดียวใช้ได้กับทุก Host ที่พูด MCP โดยไม่ต้องแก้ Kokoro เลย

<a id="ch3-1"></a>
### 3.1 วิธีเรียก MCP tool ผ่าน Host: prompt → `tools/list` → `tools/call` → ผลลัพธ์

ก่อนเรียกต้องลงทะเบียน server กับ Host ก่อน (บทที่ 4 ตัวอย่างไฟล์ตั้งค่า [`labs/my-mcp-server/mcp.json`](labs/my-mcp-server/mcp.json) สำหรับ Claude Code และ [`codex-config-snippet.toml`](labs/my-mcp-server/codex-config-snippet.toml) สำหรับ Codex) ระบุ `command` เป็น python ของ venv และ `args` เป็น path ของ `tts_server.py` เมื่อเปิด Host ใหม่ Host จะเปิด server เป็น subprocess แล้วทำ `initialize` และ `tools/list` ให้เองทันที ข้อควรระวังตอนนี้: stdout ของ server เป็นของ JSON-RPC ทั้งสาย ถ้า `print()` หรือมี `WARNING` ของไลบรารีหลุดลง stdout ข้อความจะเสียและ Host ตัดการเชื่อมต่อ ให้เขียนลง stderr แทน (ข้อ 4.7)

**1. Prompt สั้น ๆ ที่ผู้ใช้พิมพ์ใน Host** (ข้อความจริงที่ใช้ทดสอบ: [`claude-tts-prompt.txt`](lab-results/own-server/run-2026-09-19-062712/claude-tts-prompt.txt))

```text
ใช้ tool speak จาก MCP server kokoro-tts สร้างเสียงจากข้อความ 'Model Context Protocol lets one server serve many agents.' แล้วบอก path ของไฟล์เสียงและความยาวเป็นวินาที
```

**2. `tools/list` — Host ค้นพบ tool** (ตัดจากข้อความจริงบนสาย [`claude-tts-wire-tts.jsonl`](lab-results/own-server/run-2026-09-19-062712/claude-tts-wire-tts.jsonl))

```json
{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
{"jsonrpc": "2.0", "id": 1, "result": {"tools": [
  {"name": "list_voices", "description": "รายชื่อเสียงที่ใช้ได้ / Available Kokoro voices.", "inputSchema": {"type": "object", "properties": {}}},
  {"name": "speak", "description": "สังเคราะห์เสียงภาษาอังกฤษจากข้อความ แล้วคืน path ของไฟล์ .wav พร้อมความยาว (วินาที)",
   "inputSchema": {"type": "object", "required": ["text"],
                   "properties": {"text": {"type": "string"}, "voice": {"type": "string", "default": "af_heart"}}}}
]}}
```

สังเกตว่าทุกอย่างในผลนี้มาจากโค้ดในบทนี้: ชื่อฟังก์ชัน docstring และ type hint โมเดลใช้ข้อมูลชุดนี้ตัดสินใจว่าจะเรียก `speak` และต้องส่ง `text` อะไร

**3. `tools/call` — โมเดลเลือก tool แล้ว Host ส่งคำสั่งเรียก** (Host ถามอนุมัติผู้ใช้ก่อน หากไม่ได้ตั้งค่าอนุญาตล่วงหน้า)

```json
{"jsonrpc": "2.0", "id": 5, "method": "tools/call",
 "params": {"name": "speak", "arguments": {"text": "Model Context Protocol lets one server serve many agents."}}}
```

โมเดลไม่ได้ส่ง `voice` มา server จึงใช้ค่าเริ่มต้น `af_heart` ตามที่ประกาศใน `inputSchema`

**4. ผลลัพธ์ — server ตอบกลับ แล้วโมเดลสรุปให้ผู้ใช้**

```json
{"jsonrpc": "2.0", "id": 5, "result": {"isError": false, "content": [{"type": "text",
 "text": "{\"path\": \".../labs/kokoro-web/audio_out/20260919-063042-63aef183.wav\", \"duration_sec\": 4.45, \"sample_rate\": 24000, \"gen_ms\": 684, \"voice\": \"af_heart\"}"}]}}
```

**ผลที่ควรได้ (expected output)** เมื่อนักศึกษาทำเอง: คำตอบสุดท้ายของ Host ต้องบอก path ไฟล์ `.wav` ในโฟลเดอร์ `labs/kokoro-web/audio_out/` และความยาวประมาณ 4.4–4.5 วินาทีสำหรับประโยคนี้ ค่า `path` (ชื่อไฟล์มี timestamp) และ `gen_ms` จะต่างกันทุกครั้งและทุกเครื่อง ส่วน `sample_rate` ต้องเป็น 24000 และ `isError` ต้องเป็น `false` ถ้าได้ `isError: true` ให้อ่านข้อความใน `content[0].text` ซึ่งเป็นสาเหตุจากฝั่ง server

**หลักฐานที่มีตอนนี้** — ทดสอบจริงด้วย Claude Code เมื่อ 19 กันยายน 2026: โมเดลเรียก `mcp__kokoro-tts__speak` 1 ครั้ง ได้ไฟล์เสียงยาว 4.45 วินาที gen 684 ms ([`claude-tts-summary.md`](lab-results/own-server/run-2026-09-19-062712/claude-tts-summary.md)) ฝั่ง Codex CLI มีไฟล์ตั้งค่าให้แล้วแต่ **ยังไม่มีผลรันจริง** ลำดับ `tools/list` → `tools/call` เป็นมาตรฐานเดียวกัน จึงคาดว่าได้ผลรูปแบบเดียวกัน แต่ต้องถือเป็นสิ่งที่ยังไม่ได้ยืนยัน

**เรียกโดยไม่ผ่านโมเดล** — ลำดับข้อความชุดเดียวกันทำได้จาก Python โดยตรง ใช้เมื่อต้องการทดสอบ server ก่อนต่อกับ Host หรือดูข้อความบนสายเต็ม ๆ ไม่ต้องคัดลอกโค้ด client มาไว้ที่นี่ ใช้สคริปต์ที่มีอยู่แล้ว:

```bash
# จากโฟลเดอร์ 03_MCP ใช้ python ของ venv ที่ติดตั้งในบทที่ 4 (/opt/venv/bin/python หรือ labs/.venv/bin/python)
labs/.venv/bin/python labs/my-mcp-server/client_test.py --server tts --wire wire-tts.jsonl   # list → call list_voices, speak
labs/.venv/bin/python labs/my-mcp-server/direct_call_kokoro.py --skip-sanity                  # call speak แล้วเปิดไฟล์ .wav ตรวจซ้ำ exit 0 = ผ่าน
```

[`client_test.py`](labs/my-mcp-server/client_test.py) ใช้ `mcp.Client` กับ `stdio_client` ของ SDK เดียวกัน (อธิบายในบทที่ 7.3) ส่วน [`direct_call_kokoro.py`](labs/my-mcp-server/direct_call_kokoro.py) เพิ่มขั้นเปิดไฟล์เสียงด้วย `soundfile` เพื่อยืนยันว่าความยาวที่ tool ตอบตรงกับไฟล์จริง ผลจริง 20 กันยายน 2026: 4.45 วินาที ตรงกันทั้งสองทาง ([`direct-call-result.json`](lab-results/documentation-check/run-2026-09-20-022330/direct-call-result.json))

---

