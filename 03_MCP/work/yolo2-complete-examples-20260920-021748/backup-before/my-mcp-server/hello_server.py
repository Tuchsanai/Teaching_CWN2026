"""
hello_server.py — MCP server ตัวแรกของนักศึกษา (Python SDK `mcp` 2.0)
=====================================================================
เปิด 3 tools, 1 resource, 1 prompt ให้ AI Agent ค้นพบและเรียกใช้ผ่าน MCP

รันแบบ stdio (ค่าเริ่มต้น — host เป็นคนเปิด process นี้เอง):
    /opt/venv/bin/python hello_server.py
รันแบบ Streamable HTTP (เปิดเป็นบริการที่ http://127.0.0.1:8766/mcp):
    /opt/venv/bin/python hello_server.py --http

สังเกต: ไม่ต้องเขียน JSON Schema เอง — type hint (a: int, b: int) และ docstring
กลายเป็น inputSchema/description ที่ client เห็นใน tools/list โดยอัตโนมัติ
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone

from mcp.server import MCPServer

mcp = MCPServer(
    "hello-lab",
    instructions="MCP server สำหรับแล็บ 03_MCP: เครื่องมือคำนวณและนับคำอย่างง่าย",
)


@mcp.tool()
def add(a: int, b: int) -> int:
    """บวกเลขจำนวนเต็มสองจำนวน / Add two integers and return the sum."""
    return a + b


@mcp.tool()
def get_time() -> str:
    """คืนเวลาปัจจุบันของเซิร์ฟเวอร์เป็น ISO 8601 (UTC) / Current server time in UTC."""
    return datetime.now(timezone.utc).isoformat()


@mcp.tool()
def count_words(text: str) -> dict:
    """นับจำนวนคำและตัวอักษรในข้อความ / Count words and characters in a text."""
    words = text.split()
    return {
        "words": len(words),
        "characters": len(text),
        "longest_word": max(words, key=len) if words else "",
    }


@mcp.resource("lab://info")
def lab_info() -> str:
    """ข้อมูลของแล็บนี้ (resource = ข้อมูลให้อ่าน ไม่ใช่การกระทำ)"""
    return (
        "hello-lab: MCP server ตัวอย่างของบทเรียน 03_MCP (KMITL). "
        "มี tools add, get_time, count_words และ prompt explain_mcp. "
        "สร้างด้วย Python SDK mcp 2.0 ใช้ transport stdio หรือ Streamable HTTP ได้"
    )


@mcp.prompt()
def explain_mcp(topic: str) -> str:
    """แม่แบบข้อความขอให้อธิบายหัวข้อเกี่ยวกับ MCP แบบเข้าใจง่าย"""
    return (
        f"อธิบายเรื่อง '{topic}' ในบริบทของ Model Context Protocol ให้นักศึกษาปีหนึ่งเข้าใจ "
        "ใช้ตัวอย่างประกอบหนึ่งตัวอย่าง และสรุปเป็นสามประโยค"
    )


if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8766)
    else:
        mcp.run()  # stdio: อ่าน JSON-RPC จาก stdin เขียนคำตอบลง stdout (ห้าม print() ลง stdout!)
