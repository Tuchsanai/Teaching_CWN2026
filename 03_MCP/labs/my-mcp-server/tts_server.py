"""
tts_server.py — "วิธีที่ 3" : เปิด Kokoro TTS เป็น MCP tool
=========================================================
ใช้ฟังก์ชัน synthesize() ตัวเดียวกับเว็บ (labs/kokoro-web/kokoro_core.py)
แต่คราวนี้ AI Agent เรียกได้โดยตรงผ่าน MCP ไม่ต้องเปิดเบราว์เซอร์และไม่ต้องรู้ URL ของ REST API

รัน (stdio):  /opt/venv/bin/python tts_server.py
"""
from __future__ import annotations

import pathlib
import sys

# ให้ import kokoro_core จากโฟลเดอร์เว็บได้ โดยไม่ต้องคัดลอกโค้ด
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "kokoro-web"))
import kokoro_core  # noqa: E402

from mcp.server import MCPServer  # noqa: E402

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
    """สังเคราะห์เสียงภาษาอังกฤษจากข้อความ แล้วคืน path ของไฟล์ .wav พร้อมความยาว (วินาที)
    Synthesize English speech with Kokoro; returns wav path, duration_sec, gen_ms."""
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
