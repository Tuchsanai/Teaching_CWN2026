"""build_whisper_lesson.py — MCP client (Streamable HTTP) เรียก whisper-cloud ผ่าน SSH tunnel
ผลลัพธ์: whisper_lesson_data.json (transcript ทั้งคลิป + คำแปลจีน + เสียง Kokoro ของ 3 นาทีแรก)"""
import asyncio, json, sys, time, pathlib
from mcp.client.client import Client

URL = sys.argv[1] if len(sys.argv) > 1 else "https://www.youtube.com/watch?v=uPKMWr1fmYs"
MCP = "http://127.0.0.1:8765/mcp"
OUT = pathlib.Path(__file__).with_name("whisper_lesson_data.json")
LIMIT = 180.0

def result(r):
    if r.is_error: raise RuntimeError(r.content[0].text if r.content else "tool error")
    if r.structured_content is not None:
        sc = r.structured_content
        return sc["result"] if isinstance(sc, dict) and set(sc) == {"result"} else sc
    return json.loads(r.content[0].text)

async def main():
    async with Client(MCP) as c:
        tools = await c.list_tools()
        print("tools:", [t.name for t in tools.tools])
        t0 = time.time()
        tr = result(await c.call_tool("transcribe_youtube", {"url": URL}, read_timeout_seconds=1200))
        print(f"transcribed: {tr['title']!r} lang={tr['language']} segments={len(tr['segments'])} in {time.time()-t0:.0f}s")
        first = [s for s in tr["segments"] if s["start"] < LIMIT]
        t0 = time.time()
        zh = result(await c.call_tool("translate_segments", {"segments": first, "source": tr["language"], "target": "zh"}, read_timeout_seconds=600))
        print(f"translated {len(zh)} segments in {time.time()-t0:.0f}s")
        t0 = time.time()
        for i, s in enumerate(zh):
            sp = result(await c.call_tool("speak_zh", {"text": s["zh"]}, read_timeout_seconds=300))
            s["audio"] = sp["audio_mp3_base64"]; s["words"] = sp["words"]; s["audio_duration"] = sp["duration"]
            print(f"  speak {i+1}/{len(zh)} {sp['duration']:.1f}s  {s['zh'][:30]}")
        print(f"kokoro done in {time.time()-t0:.0f}s")
        data = {"url": URL, "video_id": tr["video_id"], "title": tr["title"], "duration": tr["duration"],
                "language": tr["language"], "limit_seconds": LIMIT, "segments": tr["segments"], "first3": zh,
                "server": "whisper-cloud (RTX 4090, Vast.ai) via Streamable HTTP", "tools": [t.name for t in tools.tools]}
        OUT.write_text(json.dumps(data, ensure_ascii=False))
        print("wrote", OUT, OUT.stat().st_size // 1024, "KB")

asyncio.run(main())
