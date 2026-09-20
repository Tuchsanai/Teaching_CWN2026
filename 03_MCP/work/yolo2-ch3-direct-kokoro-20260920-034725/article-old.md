<a id="ch3"></a>
## บทที่ 3 เรียกใช้ Kokoro ผ่าน MCP ด้วย `MCPServer`

ตัวอย่างนี้เปิดความสามารถ **สังเคราะห์เสียงภาษาอังกฤษด้วย Kokoro-82M** เป็น MCP tool ชื่อ `speak` เพื่อให้ Host ค้นพบและเรียกใช้งานได้ โค้ดฉบับเต็มอยู่ที่ [`tts_server.py`](labs/my-mcp-server/tts_server.py)

**สร้าง MCP server** — ตัวอย่างย่อด้านล่างใช้ตำแหน่งไฟล์ `labs/my-mcp-server/tts_server.py` และเรียก `kokoro_core` ภายใน server ต้องมีโฟลเดอร์ `labs/` และติดตั้งแพ็กเกจตามบทที่ 4 ก่อน จึงจะรันได้

```python
import pathlib
import sys
from mcp.server import MCPServer

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "kokoro-web"))
import kokoro_core

mcp = MCPServer("kokoro-tts", instructions="สร้างเสียงภาษาอังกฤษด้วย Kokoro-82M")

@mcp.tool()
def speak(text: str, voice: str = "af_heart") -> dict:
    """สร้างเสียงจากข้อความ แล้วคืน path ของไฟล์ .wav และข้อมูลเสียง"""
    r = kokoro_core.synthesize(text, voice)
    return {
        "path": r["path"],
        "duration_sec": r["duration_sec"],
        "sample_rate": r["sample_rate"],
        "gen_ms": r["gen_ms"],
        "voice": r["voice"],
    }

if __name__ == "__main__":
    mcp.run()
```

- `MCPServer(...)` สร้าง server พร้อมชื่อและคำแนะนำการใช้งาน โดยใช้คลาสจาก MCP Python SDK 2.x ของบทเรียน
- `@mcp.tool()` ประกาศฟังก์ชันเป็น tool: docstring เป็นคำอธิบาย และ type hint ช่วยสร้าง `inputSchema` โดย `text` จำเป็น ส่วน `voice` มีค่าเริ่มต้น
- `mcp.run()` เริ่มรับข้อความผ่าน **stdio** ให้ Host เปิด server เป็น subprocess ได้ ห้ามพิมพ์ log ลง stdout เพราะเป็นช่องส่ง JSON-RPC ให้ใช้ stderr แทน

<a id="ch3-1"></a>
### 3.1 เรียก MCP tool ผ่าน Host

ลงทะเบียน `kokoro-tts` ตามบทที่ 4 โดยให้ `command` เป็น Python ของ venv และ `args` ชี้ไปที่ `tts_server.py` จากนั้นเปิด Host session ใหม่ แล้วส่งคำขอ:

```text
ใช้ tool speak ของ kokoro-tts สร้างเสียงจากข้อความ
"Model Context Protocol lets one server serve many agents."
แล้วบอก path ของไฟล์เสียงและความยาวเป็นวินาที
```

**ลำดับการทำงาน:** Host เรียก `tools/list` เพื่อรู้จัก `speak` → โมเดลเลือก tool และ argument → Host ตรวจนโยบายอนุมัติแล้วส่ง `tools/call` → server สร้างเสียงและคืนผลให้ Host สรุป

**ผลที่ควรได้:** path ของไฟล์ `.wav`, `duration_sec`, `sample_rate`, `gen_ms` และ `voice` โดยไฟล์เสียงต้องเปิดได้และความยาวมากกว่า 0 หากผล tool มี `isError: true` ให้ตรวจข้อความ error ก่อนถือว่าผ่าน

หลักฐานเดิมจาก Claude Code ได้เสียงยาว **4.45 วินาที** ที่ **24000 Hz** ([ผลการทดลอง](lab-results/own-server/run-2026-09-19-062712/claude-tts-summary.md)) ตัวเลขนี้เป็นผลรอบที่บันทึกไว้ ส่วน Codex CLI ยังไม่มีผลทดสอบจริง

**ทดสอบผ่าน MCP client โดยไม่ใช้โมเดล** — หลังติดตั้งบทที่ 4 รันจากโฟลเดอร์ `03_MCP`:

```bash
labs/.venv/bin/python labs/my-mcp-server/direct_call_kokoro.py --skip-sanity
```

สคริปต์ [`direct_call_kokoro.py`](labs/my-mcp-server/direct_call_kokoro.py) เรียก **MCP server ฉบับเต็มที่มีอยู่ในแล็บ** ผ่าน `tools/list` และ `tools/call` แล้วตรวจไฟล์เสียงจริง ไม่ใช่เรียกฟังก์ชัน Kokoro โดยตรง (รายละเอียด client ดูบทที่ 7.3)

---

