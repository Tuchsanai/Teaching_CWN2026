"""
client_test.py — MCP client ทดสอบ server ของเราเอง (ไม่ต้องใช้ LLM)
==================================================================
ทำหน้าที่เหมือน "MCP Client" ใน host: เชื่อมต่อ → ค้นพบ (tools/list, resources/list,
prompts/list) → เรียกใช้ (tools/call, resources/read, prompts/get)

    python client_test.py --server hello                 # stdio ตรง ๆ
    python client_test.py --server hello --wire w.jsonl  # stdio ผ่าน wire_capture.py (บันทึกข้อความบนสาย)
    python client_test.py --server tts   --wire w.jsonl
    python client_test.py --server http                  # ต่อ http://127.0.0.1:8766/mcp (รัน hello_server.py --http ก่อน)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import pathlib
import sys

from mcp import Client
from mcp.client.stdio import StdioServerParameters, stdio_client

HERE = pathlib.Path(__file__).resolve().parent
PY = sys.executable
SENTENCE = "Model Context Protocol lets one server serve many agents"


def dump(obj) -> str:
    if hasattr(obj, "model_dump"):
        obj = obj.model_dump(by_alias=True, exclude_none=True, mode="json")
    return json.dumps(obj, ensure_ascii=False, indent=2)


def make_target(server: str, wire: str | None):
    if server == "http":
        return "http://127.0.0.1:8766/mcp"
    script = HERE / ("hello_server.py" if server == "hello" else "tts_server.py")
    if wire:
        args = [str(HERE / "wire_capture.py"), "--log", wire, "--", PY, str(script)]
    else:
        args = [str(script)]
    return stdio_client(StdioServerParameters(command=PY, args=args))


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", choices=["hello", "tts", "http"], default="hello")
    ap.add_argument("--wire", default=None, help="jsonl path: บันทึกข้อความบนสายผ่าน wire_capture.py")
    a = ap.parse_args()

    async with Client(make_target(a.server, a.wire)) as client:
        print("== connected ==")
        print("protocol_version:", client.protocol_version)
        print("server_info:", dump(client.server_info))
        print("server_capabilities:", dump(client.server_capabilities))
        print("instructions:", client.instructions)

        print("\n== tools/list ==")
        tools = await client.list_tools()
        for t in tools.tools:
            print(dump({"name": t.name, "description": t.description, "inputSchema": t.input_schema}))

        print("\n== resources/list ==")
        print(dump(await client.list_resources()))
        print("\n== prompts/list ==")
        print(dump(await client.list_prompts()))

        if a.server in ("hello", "http"):
            print("\n== tools/call add(17, 25) ==")
            print(dump(await client.call_tool("add", {"a": 17, "b": 25})))
            print("\n== tools/call get_time() ==")
            print(dump(await client.call_tool("get_time", {})))
            print(f"\n== tools/call count_words({SENTENCE!r}) ==")
            print(dump(await client.call_tool("count_words", {"text": SENTENCE})))
            print("\n== resources/read lab://info ==")
            print(dump(await client.read_resource("lab://info")))
            print("\n== prompts/get explain_mcp(topic='tools/call') ==")
            print(dump(await client.get_prompt("explain_mcp", {"topic": "tools/call"})))
        else:
            print("\n== tools/call list_voices() ==")
            print(dump(await client.call_tool("list_voices", {})))
            print(f"\n== tools/call speak({SENTENCE + '.'!r}) ==")
            print(dump(await client.call_tool("speak", {"text": SENTENCE + ".", "voice": "af_heart"})))
    print("\n== disconnected ==")


if __name__ == "__main__":
    asyncio.run(main())
