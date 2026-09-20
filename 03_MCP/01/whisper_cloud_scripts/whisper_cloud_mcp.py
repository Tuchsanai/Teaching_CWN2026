"""whisper_cloud_mcp.py — MCP server (Streamable HTTP) บน GPU cloud
tools: transcribe_youtube · translate_segments · speak_zh
"""
import base64, contextlib, io, os, pathlib, re, subprocess, sys, time, uuid

import numpy as np
import soundfile as sf
from mcp.server import MCPServer

WORK = pathlib.Path("/root/work"); WORK.mkdir(exist_ok=True)
_whisper = _nllb = _kokoro = None

def log(*a): print(*a, file=sys.stderr, flush=True)

# ---------- โมเดล (โหลดครั้งแรกที่ใช้) ----------
def whisper():
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel
        t = time.time(); _whisper = WhisperModel("large-v3", device="cuda", compute_type="float16")
        log(f"whisper large-v3 loaded {time.time()-t:.1f}s")
    return _whisper

def nllb():
    global _nllb
    if _nllb is None:
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        mid = "facebook/nllb-200-distilled-600M"
        t = time.time()
        tok = AutoTokenizer.from_pretrained(mid)
        model = AutoModelForSeq2SeqLM.from_pretrained(mid, torch_dtype=torch.float16).to("cuda").eval()
        _nllb = (tok, model); log(f"nllb loaded {time.time()-t:.1f}s")
    return _nllb

def kokoro():
    global _kokoro
    if _kokoro is None:
        with contextlib.redirect_stdout(sys.stderr):
            from kokoro import KPipeline
            _kokoro = KPipeline(lang_code="z", repo_id="hexgrad/Kokoro-82M")
    return _kokoro

# ---------- tools ----------
mcp = MCPServer("whisper-cloud", instructions="ถอดเสียง YouTube ด้วย Whisper large-v3, แปลด้วย NLLB, อ่านจีนด้วย Kokoro (GPU)")

@mcp.tool()
def transcribe_youtube(url: str, language: str = "auto") -> dict:
    """ดาวน์โหลดเสียงจาก YouTube แล้วถอดเสียงทั้งคลิปด้วย Whisper large-v3 (GPU)
    คืน title, duration, language ที่ตรวจพบ และ segments [{start, end, text}] (วินาที)
    language: "auto" ให้ Whisper ตรวจเอง หรือระบุ เช่น "th" "en" "zh"
    """
    vid = re.search(r"(?:v=|youtu\.be/)([\w-]{11})", url)
    vid = vid.group(1) if vid else uuid.uuid4().hex[:11]
    audio = WORK / f"{vid}.audio"
    meta = {"title": vid, "duration": None}
    if not audio.exists():
        r = subprocess.run(["/root/venv/bin/yt-dlp", "-f", "bestaudio", "-o", str(audio),
                            "--print-to-file", "%(title)s\t%(duration)s", str(WORK / f"{vid}.meta"), url],
                           capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            fb = pathlib.Path("/root/yt_audio.webm")          # fallback: ไฟล์ที่ push มาจากเครื่องผู้ใช้
            if not fb.exists():
                raise ValueError("yt-dlp failed: " + r.stderr[-800:])
            log("yt-dlp failed, using uploaded fallback"); audio.write_bytes(fb.read_bytes())
    mf = WORK / f"{vid}.meta"
    if mf.exists():
        t, _, d = mf.read_text().strip().rpartition("\t"); meta = {"title": t, "duration": float(d) if d else None}
    cache = WORK / f"{vid}.{language}.json"
    if cache.exists():
        log("cache hit"); import json; return json.loads(cache.read_text())
    wav = WORK / f"{vid}.wav"
    if not wav.exists():
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(audio), "-ac", "1", "-ar", "16000", str(wav)], check=True)
    t0 = time.time()
    segs, info = whisper().transcribe(str(wav), language=None if language == "auto" else language,
                                      vad_filter=True, beam_size=5)
    out = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in segs if s.text.strip()]
    log(f"transcribed {len(out)} segments in {time.time()-t0:.1f}s lang={info.language}")
    res = {"video_id": vid, "title": meta["title"], "duration": meta["duration"] or round(info.duration, 1),
           "language": info.language, "language_probability": round(info.language_probability, 3),
           "segments": out, "seconds_used": round(time.time() - t0, 1)}
    import json; cache.write_text(json.dumps(res, ensure_ascii=False))
    return res

LANG = {"th": "tha_Thai", "en": "eng_Latn", "zh": "zho_Hans", "ja": "jpn_Jpan", "ko": "kor_Hang"}

@mcp.tool()
def translate_segments(segments: list[dict], source: str = "th", target: str = "zh") -> list[dict]:
    """แปล text ของทุก segment ด้วย NLLB-200 (GPU) คืน list เดิมที่เพิ่ม field "zh" (หรือชื่อ target)
    source/target ใช้รหัสสั้น th en zh ja ko หรือรหัส NLLB เต็มเช่น tha_Thai
    """
    import torch
    tok, model = nllb()
    src, tgt = LANG.get(source, source), LANG.get(target, target)
    tok.src_lang = src
    texts = [s["text"] for s in segments]
    outs = []
    for i in range(0, len(texts), 16):
        batch = tok(texts[i:i+16], return_tensors="pt", padding=True, truncation=True, max_length=256).to("cuda")
        with torch.no_grad():
            gen = model.generate(**batch, forced_bos_token_id=tok.convert_tokens_to_ids(tgt), max_new_tokens=256, num_beams=4)
        outs += tok.batch_decode(gen, skip_special_tokens=True)
    key = target if len(target) <= 3 else target[:2]
    return [dict(s, **{key: o}) for s, o in zip(segments, outs)]

@mcp.tool()
def speak_zh(text: str, voice: str = "zf_xiaoxiao", gap_ms: int = 40) -> dict:
    """อ่านข้อความจีนด้วย Kokoro แบบสังเคราะห์ทีละคำแล้วต่อเสียงกัน จึงรู้เวลาเริ่ม-จบของทุกคำ
    คืน audio_mp3_base64 (mono 24 kHz), duration, words [{word, pinyin, start, end}] (เครื่องหมายวรรคตอนมี start=end)
    """
    import jieba
    from pypinyin import lazy_pinyin, Style
    pipe = kokoro(); sr = 24000
    tokens = [w for w in jieba.lcut(text) if w.strip()]
    gap = np.zeros(int(sr * gap_ms / 1000), dtype=np.float32)
    chunks, words, cur = [], [], 0.0
    for w in tokens:
        if not re.search(r"[一-鿿A-Za-z0-9]", w):        # เครื่องหมายวรรคตอน: ไม่มีเสียง
            words.append({"word": w, "pinyin": "", "start": round(cur, 3), "end": round(cur, 3)}); continue
        audio = None
        with contextlib.redirect_stdout(sys.stderr):
            for _, _, a in pipe(w, voice=voice):
                a = a.detach().cpu().numpy().astype(np.float32) if hasattr(a, "detach") else np.asarray(a, dtype=np.float32)
                audio = a if audio is None else np.concatenate([audio, a])
        if audio is None: audio = gap
        # ตัดความเงียบหัว-ท้ายของแต่ละคำ ให้ไฮไลต์ตรงเสียงจริง
        nz = np.where(np.abs(audio) > 0.01)[0]
        if len(nz): audio = audio[max(0, nz[0]-240): nz[-1]+480]
        dur = len(audio) / sr
        words.append({"word": w, "pinyin": " ".join(lazy_pinyin(w, style=Style.TONE)), "start": round(cur, 3), "end": round(cur + dur, 3)})
        chunks += [audio, gap]; cur += dur + gap_ms / 1000
    full = np.concatenate(chunks) if chunks else gap
    wav = io.BytesIO(); sf.write(wav, full, sr, format="WAV", subtype="PCM_16")
    mp3 = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", "pipe:0", "-codec:a", "libmp3lame", "-b:a", "64k", "-f", "mp3", "pipe:1"],
                         input=wav.getvalue(), capture_output=True, check=True).stdout
    return {"text": text, "voice": voice, "sample_rate": sr, "duration": round(len(full) / sr, 3),
            "words": words, "audio_mp3_base64": base64.b64encode(mp3).decode()}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8765"))
    log(f"whisper-cloud listening on http://127.0.0.1:{port}/mcp")
    mcp.run(transport="streamable-http", host="127.0.0.1", port=port, max_request_body_size=64 * 1024 * 1024)
