"""
summarize_stream.py — สรุปไฟล์ stream-json ของ `claude -p --output-format stream-json --verbose`
ให้เป็น Markdown: tool ที่ถูกเรียก (ชื่อ + argument), ผลที่ tool ตอบ, คำตอบสุดท้าย, โมเดล และ usage

    python summarize_stream.py claude-use-stream.jsonl > claude-use-summary.md
"""
from __future__ import annotations

import json
import sys


def main(path: str) -> None:
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    tool_uses: dict[str, dict] = {}
    order: list[str] = []
    results: dict[str, str] = {}
    model = None
    mcp_servers = None
    final = None
    usage = None
    cost = None
    duration_ms = None
    num_turns = None
    texts: list[str] = []

    for ev in events:
        t = ev.get("type")
        if t == "system" and ev.get("subtype") == "init":
            model = ev.get("model")
            mcp_servers = ev.get("mcp_servers")
            tools = [x for x in ev.get("tools", []) if str(x).startswith("mcp__")]
            init_tools = tools
        elif t == "assistant":
            msg = ev.get("message", {})
            model = model or msg.get("model")
            for block in msg.get("content", []):
                if block.get("type") == "tool_use":
                    tool_uses[block["id"]] = {"name": block["name"], "input": block.get("input")}
                    order.append(block["id"])
                elif block.get("type") == "text":
                    texts.append(block.get("text", ""))
        elif t == "user":
            msg = ev.get("message", {})
            content = msg.get("content", [])
            if isinstance(content, list):
                for block in content:
                    if block.get("type") == "tool_result":
                        c = block.get("content")
                        if isinstance(c, list):
                            c = "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
                        results[block["tool_use_id"]] = str(c)
        elif t == "result":
            final = ev.get("result")
            usage = ev.get("usage")
            cost = ev.get("total_cost_usd")
            duration_ms = ev.get("duration_ms")
            num_turns = ev.get("num_turns")

    print(f"# สรุปการรัน Claude Code: `{path.split('/')[-1]}`\n")
    print(f"- โมเดล: `{model}`")
    print(f"- MCP servers ที่เชื่อมต่อ (จาก system/init): `{json.dumps(mcp_servers, ensure_ascii=False)}`")
    try:
        print(f"- MCP tools ที่ host มองเห็น: {', '.join('`'+x+'`' for x in init_tools)}")
    except NameError:
        pass
    print(f"- จำนวน turn: {num_turns} · เวลา: {duration_ms} ms · usage: `{json.dumps(usage, ensure_ascii=False)}` · cost: {cost}\n")
    print(f"## tool ที่ถูกเรียก ({len(order)} ครั้ง)\n")
    print("| # | tool | input | ผลที่ server ตอบ (ตัดที่ 300 ตัวอักษร) |\n| --- | --- | --- | --- |")
    for i, tid in enumerate(order, 1):
        tu = tool_uses[tid]
        res = results.get(tid, "").replace("\n", " ").replace("|", "\\|")
        print(f"| {i} | `{tu['name']}` | `{json.dumps(tu['input'], ensure_ascii=False)}` | {res[:300]} |")
    print("\n## คำตอบสุดท้ายของ Claude\n")
    print(final if final is not None else "\n\n".join(texts))


if __name__ == "__main__":
    main(sys.argv[1])
