"""
kokoro_core.py — "วิธีที่ 1" : Python function ธรรมดา
=====================================================
ฟังก์ชัน synthesize() สังเคราะห์เสียงภาษาอังกฤษด้วย Kokoro-82M (https://github.com/hexgrad/kokoro)
ไฟล์นี้ถูกใช้ซ้ำโดย
  - app.py        → เปิดเป็น REST API  (วิธีที่ 2)
  - tts_server.py → เปิดเป็น MCP tool  (วิธีที่ 3)
เพื่อให้นักศึกษาเห็นว่า "ความสามารถเดียวกัน" ถูกเปิดให้เรียกใช้ได้ 3 แบบ

ข้อจำกัด: Kokoro รองรับภาษาอังกฤษ (และอีกไม่กี่ภาษา) ยังไม่รองรับภาษาไทย
"""
from __future__ import annotations

import os
import pathlib
import threading
import time
import uuid

import numpy as np
import soundfile as sf
import torch

BASE_DIR = pathlib.Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "audio_out"          # ไฟล์ .wav ที่สร้างจะอยู่ที่นี่
SAMPLE_RATE = 24_000                         # Kokoro ให้เสียงที่ 24 kHz เสมอ
VOICES = ["af_heart", "af_bella", "am_adam", "am_michael"]  # เสียงที่ทดสอบแล้วว่าโหลดได้
MAX_CHARS = 500

# เลือกอุปกรณ์: ค่าเริ่มต้น cpu (เร็วพอสำหรับประโยคสั้น ๆ และไม่มีปัญหา driver)
# ถ้าตั้ง KOKORO_DEVICE=cuda บนเครื่องนี้ (RTX 5090 + torch nightly) ต้องปิด cuDNN ก่อน
# ไม่งั้นจะเจอ "RuntimeError: GET was unable to find an engine to execute this computation"
DEVICE = os.environ.get("KOKORO_DEVICE", "cpu")

_pipeline = None
_lock = threading.Lock()


def get_pipeline():
    """โหลดโมเดลครั้งเดียว (lazy) แล้วใช้ซ้ำ — thread-safe"""
    global _pipeline
    with _lock:
        if _pipeline is None:
            if DEVICE.startswith("cuda"):
                torch.backends.cudnn.enabled = False
            from kokoro import KPipeline  # import ช้า จึงทำเมื่อจำเป็น
            _pipeline = KPipeline(lang_code="a", device=DEVICE)  # 'a' = American English
    return _pipeline


def synthesize(text: str, voice: str = "af_heart") -> dict:
    """แปลงข้อความภาษาอังกฤษเป็นไฟล์เสียง .wav

    คืนค่า dict: path, filename, duration_sec, sample_rate, gen_ms, voice, text
    โยน ValueError เมื่อข้อความว่าง/ยาวเกิน หรือชื่อเสียงไม่รู้จัก
    """
    text = (text or "").strip()
    if not text:
        raise ValueError("text must not be empty")
    if len(text) > MAX_CHARS:
        raise ValueError(f"text too long ({len(text)} > {MAX_CHARS} characters)")
    if voice not in VOICES:
        raise ValueError(f"unknown voice '{voice}', choose one of {VOICES}")

    pipe = get_pipeline()
    t0 = time.perf_counter()
    chunks = []
    for _graphemes, _phonemes, audio in pipe(text, voice=voice, speed=1.0):
        chunks.append(audio.numpy() if hasattr(audio, "numpy") else np.asarray(audio))
    wav = np.concatenate(chunks) if chunks else np.zeros(0, dtype=np.float32)
    gen_ms = round((time.perf_counter() - t0) * 1000)

    AUDIO_DIR.mkdir(exist_ok=True)
    filename = f"{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}.wav"
    path = AUDIO_DIR / filename
    sf.write(str(path), wav, SAMPLE_RATE)

    return {
        "path": str(path),
        "filename": filename,
        "duration_sec": round(len(wav) / SAMPLE_RATE, 2),
        "sample_rate": SAMPLE_RATE,
        "gen_ms": gen_ms,
        "voice": voice,
        "text": text,
        "device": DEVICE,
    }


if __name__ == "__main__":
    # ทดลองเรียกเป็น Python function ตรง ๆ:  python kokoro_core.py "Hello world"
    import json
    import sys

    print(json.dumps(synthesize(" ".join(sys.argv[1:]) or "Hello from Kokoro."), indent=2))
