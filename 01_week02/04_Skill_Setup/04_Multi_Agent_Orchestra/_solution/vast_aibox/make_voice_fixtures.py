"""make_voice_fixtures.py — สร้างไฟล์เสียง "ลูกค้า" สำหรับ e2e จาก ai-box ที่รันอยู่

อ่าน  <fixtures>/questions.json   [{id, text, lang}]
เขียน <fixtures>/<id>.wav          16 kHz mono PCM16 + เงียบ 0.4 วิ หัว-ท้าย
      <fixtures>/index.json        {"<sha256 ของไฟล์ wav>": {id, text, language, file, durationMs}}

เสียงลูกค้า = VoxCPM2 voice design (ผู้หญิงไทยวัยทำงาน) — คนละเสียงกับมาสคอต "nongchang" (ผู้ชายเสียงสดใส)
แต่ละไฟล์ตรวจกลับด้วย Whisper ของ ai-box: CER > 0.15 → สุ่ม seed ใหม่ (สูงสุด 5 ครั้ง)

ใช้:  AIBOX_URL=http://localhost:8090 AIBOX_API_KEY=... python make_voice_fixtures.py <fixtures dir> [--only V09,V10]
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
import bench  # noqa: E402  (ใช้ client + CER ตัวเดียวกับ bench)

VOICE = {
    "th": "A Thai woman in her thirties, a homeowner shopping for building materials, natural relaxed "
          "conversational tone, normal pace, clear Central Thai",
    "en": "A Thai woman in her thirties speaking English with a light Thai accent, natural conversational tone",
}
PAD_S = 0.4
SR = 16000


def make_one(q: dict) -> tuple[bytes, float, int, str]:
    lang = q.get("lang", "th")
    best = None
    for attempt in range(5):
        seed = 1000 + attempt * 17 + sum(map(ord, q["id"]))
        b, _ = bench.api_tts(q["text"], voice="customer", instructions=VOICE.get(lang, VOICE["th"]),
                             seed=seed, sample_rate=SR, language=lang)
        y, sr = sf.read(io.BytesIO(b), dtype="float32")
        assert sr == SR, sr
        pad = np.zeros(int(PAD_S * SR), dtype=np.float32)
        y = np.concatenate([pad, y, pad])
        buf = io.BytesIO()
        sf.write(buf, y, SR, format="WAV", subtype="PCM_16")
        wav = buf.getvalue()
        tr = bench.api_stt(wav, lang)["text"]
        c = bench.cer(tr, q["text"]) if lang == "th" else bench.wer(tr, q["text"])
        print(f"  {q['id']} try{attempt} seed={seed} dur={len(y) / SR:.2f}s err={c:.3f} → {tr}", flush=True)
        if best is None or c < best[1]:
            best = (wav, c, seed, tr)
        if c <= 0.15:
            break
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fixtures", nargs="?", default=str(Path(__file__).resolve().parents[1] / "buildmart/e2e/voice-fixtures"))
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    d = Path(a.fixtures)
    qs = json.loads((d / "questions.json").read_text(encoding="utf-8"))
    only = set(filter(None, a.only.split(",")))
    for q in qs:
        if only and q["id"] not in only and (d / f"{q['id']}.wav").exists():
            continue
        wav, err, seed, tr = make_one(q)
        (d / f"{q['id']}.wav").write_bytes(wav)
        print(f"{q['id']}: err={err:.3f} seed={seed}", flush=True)
    # index.json จากไฟล์จริงทุกไฟล์ใน questions.json
    index = {}
    for q in qs:
        wav = (d / f"{q['id']}.wav").read_bytes()
        info = sf.info(io.BytesIO(wav))
        index[hashlib.sha256(wav).hexdigest()] = {
            "id": q["id"], "text": q["text"], "language": q.get("lang", "th"),
            "file": f"{q['id']}.wav", "durationMs": int(round(info.frames / info.samplerate * 1000))}
    (d / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"index.json: {len(index)} entries")


if __name__ == "__main__":
    os.environ.setdefault("AIBOX_URL", "http://localhost:8090")
    main()
