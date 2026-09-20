import pathlib, re
root = pathlib.Path("/root/workspace/CWN/Teaching/03_MCP")
run = "lab-results/documentation-check/run-2026-09-20-022330"
code = (root/"labs/my-mcp-server/direct_call_kokoro.py").read_text(encoding="utf-8").rstrip("\n")
stdout = (root/run/"direct-call-stdout.txt").read_text(encoding="utf-8").rstrip("\n")
bad = (root/run/"direct-call-badvoice-stderr.txt").read_text(encoding="utf-8")
badline = [l for l in bad.splitlines() if l.startswith("[FAIL]")][0]
assert "```" not in code and "```" not in stdout

sec = f"""### 3.1 โค้ดเรียก MCP ตรง ๆ ฉบับเต็ม (คัดลอกแล้วรันได้)

ตารางด้านบนบอกว่า MCP ต่างจาก function/API อย่างไร ส่วนนี้พิสูจน์ด้วยโค้ดที่รันได้จริง: เขียน **MCP Client ด้วยมือ 1 ไฟล์** ทำหน้าที่แทน Host (Claude Code / Codex) แล้วเรียก **tool `speak` ของ `kokoro-tts`** ซึ่งเป็น "แบบที่ 3" ในหัวข้อนี้ พร้อม sanity check ด้วย `add` ของ `hello-lab` ก่อน เพื่อแยกให้ออกว่าถ้าพังคือพังที่เส้นทาง MCP หรือพังที่ Kokoro ทั้งสอง server เป็นของจริงในโฟลเดอร์ [`labs/my-mcp-server/`](labs/my-mcp-server/) ไม่ใช่ API สมมติ

**บริบทก่อนรัน**

| สิ่งที่ต้องรู้ | ค่าที่ใช้ |
| --- | --- |
| working directory ของทุกคำสั่ง | โฟลเดอร์บทเรียน `03_MCP` (บนเครื่องผู้สอนคือ `/root/workspace/CWN/Teaching/03_MCP`) เอกสารนี้แทนด้วย `<PATH_TO_03_MCP>` |
| ตัวแปลภาษา Python | `/opt/venv/bin/python` (เครื่องเรียนของผู้สอน) หรือ `labs/.venv/bin/python` ถ้าติดตั้งเองตามข้อ 4.6.2 |
| แพ็กเกจที่ต้องมี | `mcp` 2.x, `kokoro`, `soundfile`, `torch` (CPU พอ) |
| ไฟล์ที่เกี่ยวข้อง | `labs/my-mcp-server/direct_call_kokoro.py` (client), `hello_server.py`, `tts_server.py`, `wire_capture.py` และ `labs/kokoro-web/kokoro_core.py` (ตัวเรียกโมเดลจริง) |
| เครือข่าย | ครั้งแรกที่เรียก `speak` ต้องต่ออินเทอร์เน็ตเพื่อดาวน์โหลดโมเดล Kokoro-82M จาก Hugging Face ครั้งถัดไปใช้แคช |
| working directory ของ **server** | ไม่ต้องสนใจ — client เปิด server เองด้วย path เต็ม และ server อ้าง path จากตำแหน่งไฟล์ตัวเอง |

ขั้นเตรียม (ตรวจก่อนว่าครบ ถ้าขั้นนี้ไม่ผ่านอย่าเพิ่งรัน client)

```bash
cd <PATH_TO_03_MCP>
ls labs/my-mcp-server/direct_call_kokoro.py labs/my-mcp-server/tts_server.py labs/kokoro-web/kokoro_core.py
/opt/venv/bin/python -c "import mcp, soundfile, kokoro; print('deps ok')"
```

**โค้ดเต็มของ client** — ไฟล์ [`labs/my-mcp-server/direct_call_kokoro.py`](labs/my-mcp-server/direct_call_kokoro.py) (แสดงครบทั้งไฟล์ ไม่มีส่วนที่ตัดออก)

```python
{code}
```

**คำสั่งรัน** (จากโฟลเดอร์ `03_MCP`)

```bash
cd <PATH_TO_03_MCP>
RUN=lab-results/documentation-check/run-$(date -u +%Y-%m-%d-%H%M%S)
mkdir -p "$RUN"
/opt/venv/bin/python labs/my-mcp-server/direct_call_kokoro.py \\
    --text "Model Context Protocol lets one server serve many agents." \\
    --voice af_heart \\
    --wire "$RUN/direct-wire.jsonl" \\
    --out  "$RUN/direct-call-result.json" \\
    > "$RUN/direct-call-stdout.txt" 2> "$RUN/direct-call-stderr.txt"
echo "exit code: $?"      # 0 = ผ่านทุกขั้น
cat "$RUN/direct-call-result.json"
```

**ผลรันจริง** (stdout ทั้งหมดของการรันเมื่อ 20 กันยายน 2026 เวลา 02:25 UTC บนเครื่องเรียน เก็บไว้ที่ [`direct-call-stdout.txt`]({run}/direct-call-stdout.txt) — exit code 0)

```text
{stdout}
```

**อธิบายทีละขั้น** — เทียบโค้ดกับข้อความ JSON-RPC ที่เกิดขึ้นจริง

| ขั้น | ในโค้ด | เกิดอะไรบนสาย | เห็นอะไรในผลรัน |
| --- | --- | --- | --- |
| 1. เลือก transport | `stdio_target()` สร้าง `StdioServerParameters(command=PY, args=[...])` | ยังไม่มีข้อความ เป็นแค่การเตรียมคำสั่งเปิด subprocess | — |
| 2. เปิดการเชื่อมต่อ | `async with Client(...)` | client เปิด server เป็นลูก แล้วทำ handshake (ใน SDK 2.x คือ `server/discover`) | `protocol_version : 2026-07-28`, `server_info` |
| 3. ค้นพบเครื่องมือ | `await client.list_tools()` | `tools/list` | `['add', 'get_time', 'count_words']` และ `['list_voices', 'speak']` พร้อม `inputSchema` ที่ SDK สร้างจาก type hint |
| 4. เรียกเครื่องมือ | `await client.call_tool("add", {{"a": 17, "b": 25}})` | `tools/call` | `42` |
| 5. เรียกงานหลัก | `await client.call_tool("speak", {{...}})` | `tools/call` ไปยัง server คนละตัว | JSON ที่มี `path`, `duration_sec`, `sample_rate`, `gen_ms`, `voice` |
| 6. ตรวจผลจริง | `verify_wav()` อ่านไฟล์ด้วย `soundfile` | ไม่ใช่ข้อความ MCP — เป็นการตรวจว่า tool ไม่ได้แต่งตัวเลข | `verified_duration_sec: 4.45`, `verified_sample_rate: 24000`, `channels: 1` |
| 7. ปิดการเชื่อมต่อ | ออกจาก `async with` | client ปิด stdin ของ server แล้ว process ของ server จบ | สคริปต์คืน exit code 0 |

จุดที่ต้องสังเกตในโค้ด

1. **`tools/call` ที่ล้มเหลวไม่โยน exception** — MCP ตอบกลับเป็นผลปกติแต่ตั้งธง `isError=true` จึงต้องมี `check_not_error()` เช็กเองทุกครั้ง ถ้าลืม โปรแกรมจะเดินต่อด้วยข้อมูลผิด
2. **ผลของ tool เป็น list ของ content block** ไม่ใช่ค่าเดี่ยว ๆ `tool_text()` จึงดึงข้อความจาก block แรกออกมาแล้วค่อย `json.loads()`
3. **SDK ใช้ task group ภายใน** ข้อผิดพลาดที่เราโยนใน `async with` จะถูกห่อมาเป็น `ExceptionGroup` ฟังก์ชัน `leaf_errors()` จึงแตกกลุ่มออกมาเพื่อพิมพ์สาเหตุจริงแทน traceback ยาว ๆ
4. **ใช้ `sys.executable`** เป็นคำสั่งเปิด server เสมอ เพื่อให้ server ใช้ venv ตัวเดียวกับ client (สาเหตุยอดฮิตของ `ModuleNotFoundError: kokoro`)
5. **ไม่ผูกกับ working directory** ทุก path อ้างจาก `pathlib.Path(__file__).resolve().parent` จะรันจากโฟลเดอร์ไหนก็ได้

**ข้อความจริงบนสาย** — ใส่ `--wire` แล้ว `wire_capture.py` จะคั่นกลางและบันทึกทุกบรรทัด ([`direct-wire.jsonl`]({run}/direct-wire.jsonl) 15 บรรทัด)

```bash
/opt/venv/bin/python - <<'PY'
import json
for line in open("{run}/direct-wire.jsonl"):
    rec = json.loads(line)
    msg = rec["msg"]
    label = msg.get("method") or f"result id={{msg.get('id')}}" if isinstance(msg, dict) else "NON-JSON: " + msg[:60]
    print(rec["dir"], "|", label)
PY
```

```text
client->server | server/discover
server->client | result id=1
client->server | tools/list
server->client | result id=2
client->server | tools/call
server->client | result id=3
client->server | server/discover
server->client | NON-JSON: WARNING: Defaulting repo_id to hexgrad/Kokoro-82M. Pass re
server->client | result id=1
client->server | tools/list
server->client | result id=2
client->server | tools/call
server->client | result id=3
client->server | tools/call
server->client | result id=4
```

บรรทัด `NON-JSON` คือกับดักจริงของ transport แบบ stdio: ไลบรารี Kokoro พิมพ์คำเตือนลง **stdout** ของ server ซึ่งเป็นช่องเดียวกับ JSON-RPC ฝั่ง client จึง log ว่า `Failed to parse JSONRPC message from server` ลง stderr ([`direct-call-stderr.txt`]({run}/direct-call-stderr.txt)) แล้วข้ามบรรทัดนั้นไป งานยังสำเร็จเพราะ SDK ทนต่อบรรทัดที่ไม่ใช่ JSON แต่ในโค้ดของเราเองต้องจำกฎนี้ให้แม่น: **server แบบ stdio ห้ามพิมพ์อะไรลง stdout นอกจาก JSON-RPC** (ดูข้อ 4.7)

**การจัดการ error — ทดสอบจริง** ส่งชื่อเสียงที่ไม่มีอยู่จริง client ตรวจกับผล `list_voices` แล้วหยุดก่อนเรียก `speak`

```bash
/opt/venv/bin/python labs/my-mcp-server/direct_call_kokoro.py --skip-sanity --voice xx_bad
echo "exit code: $?"
```

```text
{badline}
exit code: 1
```

หลักฐานอยู่ที่ [`direct-call-badvoice-stderr.txt`]({run}/direct-call-badvoice-stderr.txt) กรณี error อื่นที่โค้ดครอบไว้: `import mcp` ไม่ได้ (บอกให้ติดตั้งและพิมพ์ว่ากำลังใช้ python ตัวไหน), ไม่พบไฟล์ server, ไม่พบ tool ที่ต้องการใน `tools/list`, tool ตอบ `isError=true`, ผลไม่ใช่ JSON และ tool คืน path ที่ไม่มีไฟล์จริง

**ฟังเสียงที่ได้จากการเรียกครั้งนี้**

<audio controls src="{run}/direct-call-kokoro.wav"></audio>

ถ้าตัวเรนเดอร์ Markdown ไม่รองรับแท็บเสียง ให้เปิดไฟล์ตรง ๆ: [`direct-call-kokoro.wav`]({run}/direct-call-kokoro.wav) (4.45 วินาที, 24000 Hz, 1 ช่อง, 213,644 ไบต์ — ตรวจซ้ำด้วย `soundfile` แล้ว)

> **ขอบเขตของหลักฐานชุดนี้:** ทั้งหมดเป็นผลของ **Python MCP client** ที่รันด้วย `/opt/venv/bin/python` ไม่ใช่ผลจาก Codex CLI เป็น Host และไม่ใช่ผลจาก Claude Code รอบนี้ การรันก่อนหน้าด้วย `client_test.py` เก็บไว้ที่ [`run-2026-09-20-021614/`](lab-results/documentation-check/run-2026-09-20-021614/) (มี `hello-stdout.txt`, `tts-stdout.txt`, wire log, [`kokoro-result.json`](lab-results/documentation-check/run-2026-09-20-021614/kokoro-result.json) และไฟล์เสียง [`kokoro-actual.wav`](lab-results/documentation-check/run-2026-09-20-021614/kokoro-actual.wav) ยาว 4.45 วินาที 24000 Hz เช่นกัน)

<audio controls src="lab-results/documentation-check/run-2026-09-20-021614/kokoro-actual.wav"></audio>

ไฟล์เสียงของรอบก่อนหน้า (ถ้าเล่นในหน้านี้ไม่ได้ ให้กดลิงก์): [`kokoro-actual.wav`](lab-results/documentation-check/run-2026-09-20-021614/kokoro-actual.wav)

"""
sec = sec.replace("{run}", run) if False else sec
p = root/"readme.md"
t = p.read_text(encoding="utf-8")
anchor = 'สรุป: MCP ไม่ได้มาแทน function หรือ API'
i = t.index(anchor)
j = t.index('\n\n---\n', i)
new = t[:j+2] + "\n" + sec.rstrip("\n") + "\n" + t[j+2:]
p.write_text(new, encoding="utf-8")
print("inserted", len(sec), "chars")
