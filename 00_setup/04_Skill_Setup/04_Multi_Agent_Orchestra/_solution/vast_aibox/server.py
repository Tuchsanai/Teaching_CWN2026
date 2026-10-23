"""ai-box — Whisper (STT) + VoxCPM2 (TTS) + bge-reranker-v2-m3 ใน FastAPI process เดียว

API ตาม CONTRACT_V3.md §2 · ทุก endpoint ยกเว้น /health ต้องมี `Authorization: Bearer $AIBOX_API_KEY`

env:
  AIBOX_API_KEY      (บังคับ) key ของ API
  MODELS             all | stt | tts | rerank | tts,rerank ...   (ค่าเริ่มต้น all)
  WHISPER_MODEL      large-v3 | large-v3-turbo                    (ค่าเริ่มต้น large-v3)
  WHISPER_COMPUTE    float16 | int8_float16                       (ค่าเริ่มต้น float16 · เร็วกว่าและแม่นกว่าเล็กน้อยจากผลวัด)
  STT_MAX_BATCH      รวมคำขอที่มาพร้อมกันเป็น batch เดียว (คลิป ≤ 30 วิ) (ค่าเริ่มต้น 8)
  STT_BATCH_WAIT_MS  รอคำขอถัดไปก่อนปิด batch                     (ค่าเริ่มต้น 25)
  STT_BEAM           beam size                                      (ค่าเริ่มต้น 5)
  TTS_TIMESTEPS      diffusion steps ของ VoxCPM2                  (ค่าเริ่มต้น 10)
  TTS_COMPILE        1 = torch.compile (เร็วขึ้น ~5 เท่า โหลดช้าขึ้น ~45 วิ) (ค่าเริ่มต้น 1)
  RERANK_MAX_LEN     token สูงสุดต่อคู่ query+passage             (ค่าเริ่มต้น 512)
"""
from __future__ import annotations

import asyncio
import io
import os
import queue
import re
import secrets
import subprocess
import sys
import threading
import time
import traceback
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf
import torch
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

API_KEY = os.environ.get("AIBOX_API_KEY", "")
_models_env = os.environ.get("MODELS", "all").replace(" ", "").lower()
ENABLED = {"stt", "tts", "rerank"} if _models_env in ("", "all") else set(_models_env.split(","))
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "large-v3")
WHISPER_COMPUTE = os.environ.get("WHISPER_COMPUTE", "float16")
WHISPER_WORKERS = int(os.environ.get("WHISPER_WORKERS", "2"))   # ทางปกติของ faster-whisper (คลิป > 30 วิ)
STT_MAX_BATCH = int(os.environ.get("STT_MAX_BATCH", "8"))
STT_BATCH_WAIT = int(os.environ.get("STT_BATCH_WAIT_MS", "25")) / 1000
STT_BEAM = int(os.environ.get("STT_BEAM", "5"))
TTS_TIMESTEPS = int(os.environ.get("TTS_TIMESTEPS", "10"))
TTS_COMPILE = os.environ.get("TTS_COMPILE", "1") == "1"
RERANK_MODEL = os.environ.get("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")
RERANK_MAX_LEN = int(os.environ.get("RERANK_MAX_LEN", "512"))
VOICES_DIR = Path(os.environ.get("VOICES_DIR", Path(__file__).parent / "voices"))

# สถานะต่อโมเดล: disabled | loading | ok | error: ...
status: dict[str, str] = {k: ("loading" if k in ENABLED else "disabled") for k in ("stt", "tts", "rerank")}
load_seconds: dict[str, float] = {}
M: dict[str, object] = {}
tts_lock = threading.Lock()      # VoxCPM2 + CUDA graphs ไม่ thread-safe → ทีละงาน
rerank_lock = threading.Lock()
stt_pool = ThreadPoolExecutor(max_workers=WHISPER_WORKERS + 2, thread_name_prefix="stt")
tts_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="tts")
rerank_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="rerank")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, file=sys.stderr, flush=True)


# ---------------------------------------------------------------- loading
def load_stt():
    from faster_whisper import WhisperModel
    M["stt"] = WhisperModel(WHISPER_MODEL, device="cuda", compute_type=WHISPER_COMPUTE,
                            num_workers=WHISPER_WORKERS)
    threading.Thread(target=_stt_batch_loop, daemon=True, name="stt-batch").start()
    stt_submit(np.zeros(16000, dtype=np.float32), "th").result()   # warm-up


# ---- STT micro-batching: คำขอที่เข้ามาพร้อมกัน (คลิป ≤ 30 วิ) ถอดใน encode()+generate() ครั้งเดียว
_stt_q: "queue.Queue[tuple]" = queue.Queue()
_stt_stats = {"batches": 0, "items": 0, "max_batch": 0}


def stt_submit(audio: np.ndarray, lang: Optional[str]) -> Future:
    fut: Future = Future()
    _stt_q.put((audio, lang, fut))
    return fut


def _stt_batch_loop():
    import ctranslate2
    from faster_whisper.audio import pad_or_trim
    from faster_whisper.tokenizer import Tokenizer
    from faster_whisper.transcribe import get_compression_ratio, get_suppressed_tokens
    m = M["stt"]
    toks: dict = {}

    def tok(lang):
        if lang not in toks:
            toks[lang] = Tokenizer(m.hf_tokenizer, m.model.is_multilingual, task="transcribe", language=lang)
        return toks[lang]
    suppress = list(get_suppressed_tokens(tok("en"), [-1]))
    while True:
        items = [_stt_q.get()]
        deadline = time.time() + STT_BATCH_WAIT
        while len(items) < STT_MAX_BATCH:
            left = deadline - time.time()
            if left <= 0:
                break
            try:
                items.append(_stt_q.get(timeout=left))
            except queue.Empty:
                break
        try:
            feats = np.stack([pad_or_trim(m.feature_extractor(a)[:, :3000]) for a, _, _ in items]).astype(np.float32)
            enc = m.model.encode(ctranslate2.StorageView.from_array(feats), to_cpu=False)
            langs = [lg for _, lg, _ in items]
            if any(lg is None for lg in langs):
                det = m.model.detect_language(enc)
                langs = [lg or det[i][0][0][2:-2] for i, lg in enumerate(langs)]
            prompts = [tok(lg).sot_sequence + [tok(lg).no_timestamps] for lg in langs]
            longest = max(len(a) for a, _, _ in items) / 16000
            max_len = min(m.max_length, len(prompts[0]) + int(longest * 25) + 24)  # ไทย ~11 token/วิ → เผื่อ 2 เท่า
            t_gen = time.time()
            res = m.model.generate(enc, prompts, beam_size=STT_BEAM, patience=1, length_penalty=1,
                                   max_length=max_len, return_scores=True, return_no_speech_prob=True,
                                   suppress_blank=True, suppress_tokens=suppress)
            if os.environ.get("STT_DEBUG"):
                log(f"stt batch n={len(items)} longest={longest:.1f}s max_len={max_len} "
                    f"tokens={[len(r.sequences_ids[0]) for r in res]} {time.time() - t_gen:.2f}s")
            _stt_stats["batches"] += 1
            _stt_stats["items"] += len(items)
            _stt_stats["max_batch"] = max(_stt_stats["max_batch"], len(items))
            for (a, _, fut), r, lg in zip(items, res, langs):
                ids = r.sequences_ids[0]
                text = tok(lg).decode(ids).strip()
                avg_lp = r.scores[0] * len(ids) / (len(ids) + 1)
                if r.no_speech_prob > 0.6 and avg_lp < -1.0:
                    text = ""                      # เงียบ/เสียงรบกวน
                elif text and get_compression_ratio(text) > cr_limit(lg):
                    _stt_stats["fallback"] = _stt_stats.get("fallback", 0) + 1
                    fut.set_result(None)           # วนซ้ำ (hallucination) → ทางปกติ (มี temperature fallback) ทำแทน
                    continue
                fut.set_result({"text": text, "language": lg})
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            for _, _, fut in items:
                if not fut.done():
                    fut.set_exception(e)


def _voice_files(name: str):
    wav, txt = VOICES_DIR / f"{name}.wav", VOICES_DIR / f"{name}.txt"
    if wav.exists() and txt.exists():
        return str(wav), txt.read_text(encoding="utf-8").strip()
    return None


def load_tts():
    from voxcpm import VoxCPM
    model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False, optimize=TTS_COMPILE)
    M["tts"] = model
    caches = {}
    for wav in sorted(VOICES_DIR.glob("*.wav")):
        vf = _voice_files(wav.stem)
        if vf:
            # โคลนแบบ "ultimate": reference (โทนเสียง) + continuation (prompt text + audio) จากไฟล์เดียวกัน
            caches[wav.stem] = model.tts_model.build_prompt_cache(
                prompt_text=vf[1], prompt_wav_path=vf[0], reference_wav_path=vf[0])
            log("voice ready:", wav.stem)
    M["voices"] = caches
    _tts_generate("ทดสอบเสียงครับ", "nongchang" if "nongchang" in caches else None, None, 1)


def load_rerank():
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(RERANK_MODEL)
    mdl = AutoModelForSequenceClassification.from_pretrained(RERANK_MODEL, torch_dtype=torch.float16).cuda().eval()
    M["rerank"] = (tok, mdl)
    _rerank("warm up", ["hello world"])


LOADERS = {"stt": load_stt, "tts": load_tts, "rerank": load_rerank}


def load_all():
    # ทีละตัว (ไม่ขนาน) — ให้วัด VRAM ต่อโมเดลได้จาก log
    for name in ("stt", "rerank", "tts"):
        if name not in ENABLED:
            continue
        t0 = time.time()
        try:
            if name == "tts":
                # CUDA graphs ของ torch.compile ผูกกับ thread → โหลดและรัน TTS ใน thread เดียวกันเสมอ (tts_pool)
                tts_pool.submit(load_tts).result()
            else:
                LOADERS[name]()
            status[name] = "ok"
            torch.cuda.synchronize()
            load_seconds[name] = round(time.time() - t0, 1)
            log(f"loaded {name} in {load_seconds[name]}s · gpu_used={gpu_mem()[0]} MiB "
                f"torch_reserved={torch.cuda.memory_reserved() // 2**20} MiB")
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            status[name] = f"error: {type(e).__name__}: {e}"[:300]


# ---------------------------------------------------------------- helpers
def gpu_mem():
    """(used_mb, total_mb) ของทั้งการ์ดจาก nvidia-smi · ถ้าไม่ได้ใช้ torch.cuda.mem_get_info"""
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=5).stdout.strip().splitlines()[0]
        u, t = (int(x) for x in out.split(","))
        return u, t
    except Exception:  # noqa: BLE001
        free, total = torch.cuda.mem_get_info()
        return (total - free) // 2**20, total // 2**20


def auth(authorization: Optional[str] = Header(default=None)):
    if not API_KEY:
        raise HTTPException(500, "AIBOX_API_KEY not set on server")
    if not authorization or not authorization.lower().startswith("bearer ") or \
            not secrets.compare_digest(authorization[7:].strip(), API_KEY):
        raise HTTPException(401, "invalid or missing bearer token")


def need(name: str):
    if status[name] != "ok":
        raise HTTPException(503, f"model '{name}' not available ({status[name]})")


def decode_audio(data: bytes, sr: int = 16000) -> np.ndarray:
    """ffmpeg: webm/ogg/wav/mp3/... → float32 mono 16 kHz"""
    p = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-i", "pipe:0",
                        "-f", "f32le", "-ac", "1", "-ar", str(sr), "pipe:1"],
                       input=data, capture_output=True, timeout=60)
    if p.returncode != 0:
        raise HTTPException(400, f"cannot decode audio: {p.stderr.decode(errors='ignore')[-300:]}")
    return np.frombuffer(p.stdout, dtype=np.float32).copy()


THAI_RE = re.compile(r"[฀-๿]")


def cr_limit(lang: Optional[str]) -> float:
    """gzip compression ratio ที่ถือว่า "วนซ้ำ" · ไทยปกติสูงถึง ~2.7 (UTF-8 3 ไบต์/ตัว) ค่า 2.4 ของ Whisper จึงเตือนผิด"""
    return 3.3 if lang in ("th", "lo", "my", "km", "zh", "ja", "ko") else 2.4


def _tts_generate(text: str, voice: Optional[str], instructions: Optional[str], seed: Optional[int]):
    model = M["tts"]
    cache = M["voices"].get(voice) if voice else None
    with tts_lock:
        if seed is not None:
            torch.manual_seed(seed)
        if cache is not None:
            # โคลนเสียงจาก prompt cache ที่สร้างไว้ตอนเริ่ม (ไม่ต้อง encode ไฟล์อ้างอิงทุกครั้ง)
            wav, _, _ = model.tts_model.generate_with_prompt_cache(
                target_text=re.sub(r"\s+", " ", text), prompt_cache=cache,
                inference_timesteps=TTS_TIMESTEPS, cfg_value=2.0, retry_badcase=True)
            wav = wav.squeeze(0).float().cpu().numpy()
        else:
            # voice design: คำบรรยายเสียงในวงเล็บนำหน้าข้อความ (ไม่ต้องมีไฟล์อ้างอิง)
            prefix = f"({instructions.strip().strip('()')})" if instructions else ""
            wav = model.generate(text=prefix + text, inference_timesteps=TTS_TIMESTEPS, cfg_value=2.0)
    return wav, model.tts_model.sample_rate


def _rerank(query: str, docs: list[str]) -> list[float]:
    tok, mdl = M["rerank"]
    scores: list[float] = []
    with rerank_lock, torch.inference_mode():
        for i in range(0, len(docs), 32):
            batch = docs[i:i + 32]
            enc = tok([[query, d] for d in batch], padding=True, truncation=True,
                      max_length=RERANK_MAX_LEN, return_tensors="pt").to("cuda")
            logits = mdl(**enc).logits.view(-1).float()
            scores += torch.sigmoid(logits).cpu().tolist()
    return scores


# ---------------------------------------------------------------- app
app = FastAPI(title="ai-box", version="3.0")


@app.on_event("startup")
def _startup():
    log(f"MODELS={sorted(ENABLED)} WHISPER_MODEL={WHISPER_MODEL} compute={WHISPER_COMPUTE} "
        f"batch={STT_MAX_BATCH} beam={STT_BEAM} TTS_COMPILE={TTS_COMPILE}")
    if not API_KEY:
        log("WARNING: AIBOX_API_KEY is empty — every protected endpoint will return 500")
    threading.Thread(target=load_all, daemon=True).start()


@app.get("/health")
def health():
    used, total = gpu_mem()
    ready = all(status[k] == "ok" for k in ENABLED)
    body = {
        "status": "ok" if ready else ("error" if any(status[k].startswith("error") for k in ENABLED) else "loading"),
        "models": dict(status),
        "vram_mb": used,
        "vram_total_mb": total,
        "torch_reserved_mb": torch.cuda.memory_reserved() // 2**20 if torch.cuda.is_available() else 0,
        "torch_max_reserved_mb": torch.cuda.max_memory_reserved() // 2**20 if torch.cuda.is_available() else 0,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "whisper_model": WHISPER_MODEL if "stt" in ENABLED else None,
        "whisper_compute": WHISPER_COMPUTE if "stt" in ENABLED else None,
        "stt_batches": dict(_stt_stats),
        "load_seconds": load_seconds,
        "voices": sorted(M.get("voices", {}).keys()),
    }
    return JSONResponse(body, status_code=200 if ready else 503)


@app.post("/v1/audio/transcriptions", dependencies=[Depends(auth)])
async def transcriptions(file: UploadFile = File(...), language: Optional[str] = Form(default=None),
                         model: Optional[str] = Form(default=None), prompt: Optional[str] = Form(default=None)):
    need("stt")
    data = await file.read()
    if not data:
        raise HTTPException(400, "empty file")
    lang = (language or "").strip().lower() or None

    loop = asyncio.get_running_loop()
    audio = await loop.run_in_executor(stt_pool, decode_audio, data)
    duration = len(audio) / 16000
    if duration < 0.1:
        return {"text": "", "language": lang or "", "duration": round(duration, 3)}
    if duration <= 29.5 and not prompt:
        r = await asyncio.wrap_future(stt_submit(audio, lang))
        if r is not None:
            return {**r, "duration": round(duration, 3)}

    def run():  # คลิปยาว / มี prompt / batch ส่งกลับมาให้ถอดใหม่
        segs, info = M["stt"].transcribe(audio, language=lang, beam_size=STT_BEAM, vad_filter=False,
                                         condition_on_previous_text=False, initial_prompt=prompt or None,
                                         compression_ratio_threshold=cr_limit(lang or "th"))
        return {"text": "".join(s.text for s in segs).strip(), "language": info.language,
                "duration": round(duration, 3)}

    return await loop.run_in_executor(stt_pool, run)


class SpeechReq(BaseModel):
    input: str = Field(..., min_length=1, max_length=2000)
    voice: str = "nongchang"
    response_format: str = "wav"
    language: Optional[str] = None          # ไม่จำเป็น: VoxCPM2 ตรวจภาษาจากข้อความเอง
    instructions: Optional[str] = None      # voice design (ใช้เมื่อ voice ไม่ใช่ไฟล์ใน voices/)
    seed: Optional[int] = None
    sample_rate: Optional[int] = None       # ค่าเริ่มต้น 48000 (ของโมเดล) · ใส่ 16000/24000 เพื่อไฟล์เล็กลง


@app.post("/v1/audio/speech", dependencies=[Depends(auth)])
async def speech(req: SpeechReq):
    need("tts")
    if req.response_format not in ("wav", "pcm"):
        raise HTTPException(400, "response_format must be wav")
    voice = req.voice if req.voice in M["voices"] else None
    if voice is None and not req.instructions:
        raise HTTPException(400, f"unknown voice '{req.voice}' (available: {sorted(M['voices'])}); "
                                 f"or pass 'instructions' for voice design")
    t0 = time.time()
    wav, sr = await asyncio.get_running_loop().run_in_executor(
        tts_pool, _tts_generate, req.input, voice, req.instructions, req.seed)
    gen_s = time.time() - t0
    if req.sample_rate and req.sample_rate != sr:
        import librosa
        wav = librosa.resample(wav, orig_sr=sr, target_sr=req.sample_rate)
        sr = req.sample_rate
    wav = np.clip(wav, -1.0, 1.0)
    buf = io.BytesIO()
    sf.write(buf, wav, sr, format="WAV", subtype="PCM_16")
    dur = len(wav) / sr
    return Response(buf.getvalue(), media_type="audio/wav", headers={
        "X-Audio-Duration": f"{dur:.3f}", "X-Gen-Seconds": f"{gen_s:.3f}",
        "X-RTF": f"{gen_s / max(dur, 1e-6):.3f}"})


class RerankReq(BaseModel):
    query: str
    documents: list[str]
    top_n: Optional[int] = None


@app.post("/v1/rerank", dependencies=[Depends(auth)])
async def rerank(req: RerankReq):
    need("rerank")
    if not req.documents:
        return {"results": []}
    scores = await asyncio.get_running_loop().run_in_executor(rerank_pool, _rerank, req.query, req.documents)
    order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    if req.top_n:
        order = order[:req.top_n]
    return {"results": [{"index": i, "relevance_score": round(scores[i], 6)} for i in order]}
