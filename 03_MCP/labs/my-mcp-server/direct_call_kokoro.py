"""
direct_call_kokoro.py — เรียก MCP tool ตรง ๆ จาก Python โดยไม่ผ่าน LLM (ฉบับเต็ม คัดลอกแล้วรันได้)
====================================================================================
ไฟล์นี้คือ "MCP Client ขนาดเล็ก" ที่ทำงานแทน Host (Claude Code / Codex) ครบทุกขั้น:

    1. เปิด MCP server ของบทเรียนเป็น subprocess แบบ stdio
    2. initialize  → ตกลงเวอร์ชันโปรโตคอลและ capabilities
    3. tools/list  → ค้นพบว่ามี tool อะไรบ้าง พร้อม inputSchema
    4. tools/call  → เรียกใช้จริง (sanity check: hello-lab add, งานหลัก: kokoro-tts speak)
    5. ตรวจไฟล์เสียงที่ได้ด้วย soundfile แล้วเขียนผลเป็น JSON

ต้องมีก่อนรัน
-------------
* Python 3.10+ ที่ติดตั้งแพ็กเกจ `mcp` 2.x, `kokoro`, `soundfile`, `torch` (CPU ก็พอ)
  - เครื่องเรียนของผู้สอนใช้ /opt/venv/bin/python
  - ถ้าทำตาม readme.md ข้อ 4.6.2 จะได้ labs/.venv/bin/python
* โฟลเดอร์ปัจจุบัน (working directory) ไม่สำคัญ เพราะสคริปต์อ้าง path จากตำแหน่งไฟล์ตัวเองเสมอ
  แต่ตัวอย่างคำสั่งด้านล่างรันจากโฟลเดอร์บทเรียน 03_MCP

วิธีรัน
-------
    # จากโฟลเดอร์ 03_MCP
    /opt/venv/bin/python labs/my-mcp-server/direct_call_kokoro.py \
        --text "Model Context Protocol lets one server serve many agents." \
        --out  lab-results/documentation-check/direct-call-result.json

    # ข้าม sanity check ของ hello-lab (เรียกเฉพาะ Kokoro)
    /opt/venv/bin/python labs/my-mcp-server/direct_call_kokoro.py --skip-sanity

    # บันทึกข้อความ JSON-RPC ทุกบรรทัดบนสายผ่าน wire_capture.py
    /opt/venv/bin/python labs/my-mcp-server/direct_call_kokoro.py --wire wire-direct.jsonl

exit code: 0 = สำเร็จทุกขั้น, 1 = มีขั้นที่ล้มเหลว (รายละเอียดพิมพ์ลง stderr)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import pathlib
import sys
import traceback

# --- แพ็กเกจของ MCP Python SDK 2.x ------------------------------------------------
# mcp.Client                      = ฝั่ง client ของโปรโตคอล (initialize/list/call)
# mcp.client.stdio.stdio_client   = transport แบบ stdio: เปิด server เป็น subprocess
try:
    from mcp import Client
    from mcp.client.stdio import StdioServerParameters, stdio_client
except ImportError as exc:  # แพ็กเกจยังไม่ได้ติดตั้ง หรือรันด้วย python ผิดตัว
    sys.exit(
        f"[FATAL] import mcp ไม่สำเร็จ: {exc}\n"
        "        ติดตั้งด้วย:  <python ของ venv> -m pip install 'mcp[cli]'\n"
        f"        python ที่ใช้อยู่ตอนนี้: {sys.executable}"
    )

HERE = pathlib.Path(__file__).resolve().parent          # .../labs/my-mcp-server
HELLO_SERVER = HERE / "hello_server.py"
TTS_SERVER = HERE / "tts_server.py"
WIRE_PROXY = HERE / "wire_capture.py"
PY = sys.executable                                      # ใช้ python ตัวเดียวกับที่รันสคริปต์นี้


def dump(obj) -> str:
    """แปลงผลลัพธ์ของ SDK (pydantic model) เป็น JSON อ่านง่าย"""
    if hasattr(obj, "model_dump"):
        obj = obj.model_dump(by_alias=True, exclude_none=True, mode="json")
    return json.dumps(obj, ensure_ascii=False, indent=2)


def stdio_target(script: pathlib.Path, wire: str | None):
    """สร้าง transport stdio ที่ชี้ไปยัง server 1 ตัว (ใส่ wire_capture.py คั่นได้)"""
    if not script.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์ server: {script}")
    args = [str(script)] if not wire else [str(WIRE_PROXY), "--log", wire, "--", PY, str(script)]
    return stdio_client(StdioServerParameters(command=PY, args=args))


def tool_text(result) -> str:
    """ดึงข้อความจาก content block แรกของผล tools/call (MCP คืนผลเป็น list ของ content)"""
    for block in getattr(result, "content", []) or []:
        text = getattr(block, "text", None)
        if text is not None:
            return text
    return ""


def check_not_error(result, label: str) -> None:
    """MCP ไม่ได้โยน exception เมื่อ tool ทำงานพลาด แต่ตั้งธง isError=true ต้องเช็กเอง"""
    if getattr(result, "is_error", False) or getattr(result, "isError", False):
        raise RuntimeError(f"tool {label} ตอบกลับด้วย isError=true: {tool_text(result)}")


async def sanity_check_hello(wire: str | None) -> dict:
    """ขั้นที่ 1 — ตรวจว่าเส้นทาง MCP ทั้งเส้นใช้งานได้ ด้วย server ที่ไม่มี dependency หนัก"""
    print("=" * 72)
    print("[1/2] sanity check — hello-lab (add)")
    print("=" * 72)
    async with Client(stdio_target(HELLO_SERVER, wire)) as client:
        print("protocol_version :", client.protocol_version)
        print("server_info      :", dump(client.server_info))

        tools = await client.list_tools()
        names = [t.name for t in tools.tools]
        print("tools/list       :", names)
        if "add" not in names:
            raise RuntimeError(f"ไม่พบ tool ชื่อ add ใน {names}")

        result = await client.call_tool("add", {"a": 17, "b": 25})
        check_not_error(result, "add")
        print("tools/call add(17, 25) →", tool_text(result))
        if tool_text(result).strip() != "42":
            raise RuntimeError(f"add(17, 25) ควรได้ 42 แต่ได้ {tool_text(result)!r}")
        return {"tools": names, "add_17_25": tool_text(result).strip()}


async def call_kokoro(text: str, voice: str, wire: str | None) -> dict:
    """ขั้นที่ 2 — งานหลักของบทที่ 3: เรียก Kokoro ผ่าน MCP (tool speak ของ kokoro-tts)"""
    print()
    print("=" * 72)
    print("[2/2] งานหลัก — kokoro-tts (speak)")
    print("=" * 72)
    async with Client(stdio_target(TTS_SERVER, wire)) as client:
        print("protocol_version :", client.protocol_version)
        print("instructions     :", client.instructions)

        tools = await client.list_tools()
        by_name = {t.name: t for t in tools.tools}
        print("tools/list       :", list(by_name))
        if "speak" not in by_name:
            raise RuntimeError(f"ไม่พบ tool ชื่อ speak ใน {list(by_name)}")
        print("inputSchema ของ speak:")
        print(dump(by_name["speak"].input_schema))

        voices = await client.call_tool("list_voices", {})
        check_not_error(voices, "list_voices")
        available = [getattr(b, "text", "") for b in (voices.content or [])]
        print("list_voices      :", available)
        if available and voice not in available:
            raise RuntimeError(f"voice {voice!r} ไม่อยู่ในรายการที่ server รองรับ: {available}")

        print(f"tools/call speak(text={text!r}, voice={voice!r}) ...")
        result = await client.call_tool("speak", {"text": text, "voice": voice})
        check_not_error(result, "speak")
        raw = tool_text(result)
        print("ผลดิบจาก tool   :", raw)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"ผลของ speak ไม่ใช่ JSON: {raw!r}") from exc
        return payload


def verify_wav(path_str: str) -> dict:
    """ขั้นสุดท้าย — เปิดไฟล์ .wav ที่ได้จริง เพื่อยืนยันว่าไม่ใช่ค่าที่ tool แต่งขึ้น"""
    path = pathlib.Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"tool คืน path มาแต่ไม่พบไฟล์จริง: {path}")
    try:
        import soundfile as sf
    except ImportError:
        print("[warn] ไม่มี soundfile จึงตรวจได้แค่ขนาดไฟล์", file=sys.stderr)
        return {"bytes": path.stat().st_size}
    info = sf.info(str(path))
    return {
        "bytes": path.stat().st_size,
        "verified_duration_sec": round(info.frames / info.samplerate, 2),
        "verified_sample_rate": info.samplerate,
        "channels": info.channels,
    }


def leaf_errors(exc: BaseException) -> list[BaseException]:
    """แตก ExceptionGroup ของ anyio ให้เหลือ error ใบสุดท้าย
    (SDK ใช้ task group ภายใน ข้อผิดพลาดที่เราโยนจึงถูกห่อมาเป็นกลุ่ม)"""
    inner = getattr(exc, "exceptions", None)
    if not inner:
        return [exc]
    out: list[BaseException] = []
    for e in inner:
        out.extend(leaf_errors(e))
    return out


async def run(args: argparse.Namespace) -> int:
    summary: dict = {"python": PY, "server_dir": str(HERE)}
    try:
        if not args.skip_sanity:
            summary["hello"] = await sanity_check_hello(args.wire)
        summary["speak"] = await call_kokoro(args.text, args.voice, args.wire)
        summary["wav"] = verify_wav(summary["speak"]["path"])
    except Exception as exc:  # noqa: BLE001 — จับทุกกรณีเพื่อรายงานสาเหตุจริงให้ผู้เรียน
        known = [e for e in leaf_errors(exc) if isinstance(e, (RuntimeError, FileNotFoundError))]
        if known:
            for e in known:
                print(f"[FAIL] {type(e).__name__}: {e}", file=sys.stderr)
        else:
            print("[FAIL] ข้อผิดพลาดที่ไม่ได้คาดไว้:", file=sys.stderr)
            traceback.print_exc()
        return 1

    print()
    print("=" * 72)
    print("สรุปผล (JSON)")
    print("=" * 72)
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    print(text)
    if args.out:
        out = pathlib.Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
        print(f"เขียนผลลง {out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="เรียก MCP tool ตรง ๆ จาก Python (ไม่ผ่าน LLM)")
    ap.add_argument("--text", default="Model Context Protocol lets one server serve many agents.",
                    help="ข้อความภาษาอังกฤษที่จะให้ Kokoro อ่าน")
    ap.add_argument("--voice", default="af_heart", help="ชื่อเสียง (ดูจาก tool list_voices)")
    ap.add_argument("--wire", default=None, help="path ไฟล์ .jsonl สำหรับบันทึกข้อความบนสาย")
    ap.add_argument("--out", default=None, help="path ไฟล์ .json สำหรับเขียนผลสรุป")
    ap.add_argument("--skip-sanity", action="store_true", help="ข้ามการตรวจ hello-lab add")
    args = ap.parse_args()
    try:
        return asyncio.run(run(args))
    except KeyboardInterrupt:
        print("ยกเลิกโดยผู้ใช้", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
