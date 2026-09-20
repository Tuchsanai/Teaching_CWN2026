<a id="ch3"></a>
## บทที่ 3 MCP ต่างจากการเรียก Python Function หรือ API โดยตรงอย่างไร

ใช้งานเดียวกันตลอดบทเรียน: **สังเคราะห์เสียงภาษาอังกฤษด้วย Kokoro-82M** เราเปิดความสามารถนี้ให้เรียกได้ 3 แบบ โดยโค้ด Kokoro ไม่ต้องแก้เลย

![งานเดียวกันเรียกได้ 3 แบบ: Python function, REST API, MCP tool](img/d04-three-ways.png)

สามบล็อกถัดไปเป็นโค้ด **ที่ตัดมาเฉพาะส่วนสำคัญ** เพื่อเทียบรูปแบบของทั้งสามวิธี (ฉบับเต็มอยู่ในไฟล์ที่ลิงก์ไว้) ส่วนโค้ดที่คัดลอกแล้วรันได้ทันทีตั้งแต่ `import` จนถึง `main()` อยู่ในข้อ [3.1](#ch3-1)

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



