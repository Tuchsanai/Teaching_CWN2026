"""
app.py — "วิธีที่ 2" : REST API ด้วย FastAPI
==========================================
เว็บทดลองสำหรับ Case Study 2 (Playwright MCP)
  GET  /             หน้าเว็บ (Text Input → ปุ่ม Speak → Result → Audio Player)
  POST /api/tts      {"text": "...", "voice": "af_heart"} → ข้อมูลไฟล์เสียง
  GET  /api/health   สถานะเซิร์ฟเวอร์และโมเดล
  GET  /api/voices   รายชื่อเสียงที่ใช้ได้
  GET  /audio/<file> ไฟล์ .wav ที่สร้างแล้ว

รัน:  ./run.sh   (หรือ  /opt/venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8765)
"""
from __future__ import annotations

import pathlib

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import kokoro_core

BASE_DIR = pathlib.Path(__file__).resolve().parent
kokoro_core.AUDIO_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Kokoro TTS Lab", version="1.0")
app.mount("/audio", StaticFiles(directory=str(kokoro_core.AUDIO_DIR)), name="audio")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


class TTSRequest(BaseModel):
    text: str
    voice: str = "af_heart"


@app.get("/")
def index():
    return FileResponse(str(BASE_DIR / "static" / "index.html"))


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "device": kokoro_core.DEVICE,
        "model_loaded": kokoro_core._pipeline is not None,
        "voices": kokoro_core.VOICES,
    }


@app.get("/api/voices")
def voices():
    return {"voices": kokoro_core.VOICES}


@app.post("/api/tts")
async def tts(req: TTSRequest):
    try:
        # งานสังเคราะห์เสียงใช้ CPU หนัก จึงรันใน threadpool ไม่ให้บล็อก event loop
        result = await run_in_threadpool(kokoro_core.synthesize, req.text, req.voice)
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    return {
        "audio_url": f"/audio/{result['filename']}",
        "duration_sec": result["duration_sec"],
        "sample_rate": result["sample_rate"],
        "gen_ms": result["gen_ms"],
        "voice": result["voice"],
        "text": result["text"],
        "device": result["device"],
    }
