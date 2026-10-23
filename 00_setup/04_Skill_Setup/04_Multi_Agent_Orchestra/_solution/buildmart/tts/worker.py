"""BuildMart tts-worker: RabbitMQ `tts.request` -> WAV in Postgres `tts_audio`.

Thai  -> PyThaiTTS (fastthaig2p, onnxruntime, in-process, preloaded)
Other -> Kokoro-FastAPI (KOKORO_URL, OpenAI-compatible /v1/audio/speech)
Reply -> exchange `chat.reply` (direct) routing key = reply_to,
         body {type:'tts', audioId, durationMs} or {type:'tts', error}
"""
import io
import json
import logging
import os
import pathlib
import threading
import time
import urllib.request
import wave

import numpy as np
import pika
import psycopg

from textnorm import clean_text, detect_lang, thai_readable

AMQP_URL = os.environ.get("AMQP_URL", "amqp://guest:guest@rabbitmq:5672")
DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://bm:bm@db:5432/buildmart")
KOKORO_URL = os.environ.get("KOKORO_URL", "http://kokoro:8880").rstrip("/")
KOKORO_VOICE = os.environ.get("KOKORO_VOICE", "af_heart")
THAI_SPEED = float(os.environ.get("THAI_SPEED", "1.0"))
HEARTBEAT_FILE = pathlib.Path(os.environ.get("HEARTBEAT_FILE", "/tmp/tts-heartbeat"))
QUEUE = "tts.request"
REPLY_EXCHANGE = "chat.reply"
SR = 24000

logging.basicConfig(level=logging.INFO, format="%(asctime)s tts-worker %(levelname)s %(message)s")
log = logging.getLogger()
logging.getLogger("pika").setLevel(logging.WARNING)

# ---------------- models ----------------
log.info("loading PyThaiTTS (fastthaig2p) ...")
from pythaitts import TTS  # noqa: E402

THAI = TTS(pretrained="fastthaig2p")
_t0 = time.time()
THAI.tts("สวัสดีครับ", speaker_idx="thai_som", return_type="waveform", preprocess=False)  # warm-up
log.info("PyThaiTTS ready (warm-up %.2fs)", time.time() - _t0)

_voice_checked = False


def kokoro_voice() -> str:
    """Prefer af_heart, fall back to af_bella / first voice if missing."""
    global _voice_checked, KOKORO_VOICE
    if _voice_checked:
        return KOKORO_VOICE
    try:
        with urllib.request.urlopen(f"{KOKORO_URL}/v1/audio/voices", timeout=10) as r:
            raw = json.load(r).get("voices", [])
        voices = [v.get("id") if isinstance(v, dict) else v for v in raw]
        if voices and KOKORO_VOICE not in voices:
            KOKORO_VOICE = "af_bella" if "af_bella" in voices else voices[0]
        _voice_checked = True
        log.info("kokoro voice = %s (%d voices)", KOKORO_VOICE, len(voices))
    except Exception as e:  # kokoro not up yet -> try again next time
        log.warning("kokoro voice list failed: %s", e)
    return KOKORO_VOICE


def to_pcm24k(samples: np.ndarray, rate: int) -> np.ndarray:
    """float32 mono any-rate -> int16 mono 24 kHz."""
    x = np.asarray(samples, dtype=np.float32).reshape(-1)
    if rate != SR and len(x):
        n = int(round(len(x) * SR / rate))
        x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)
    return (np.clip(x, -1.0, 1.0) * 32767).astype(np.int16)


def wav_bytes(pcm: np.ndarray) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


def read_wav(data: bytes):
    with wave.open(io.BytesIO(data), "rb") as w:
        ch, sw, rate, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    if sw == 2:
        x = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    elif sw == 4:
        x = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648.0
    elif sw == 1:
        x = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128) / 128.0
    else:
        raise ValueError(f"unsupported sample width {sw}")
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    return x, rate


def synth_th(text: str) -> np.ndarray:
    spoken = thai_readable(text)
    chunks = THAI.stream(spoken, speaker_idx="thai_som", return_type="waveform",
                         preprocess=True, max_phonemes=400, speed=THAI_SPEED)
    gap = np.zeros(int(SR * 0.12), dtype=np.float32)
    parts = []
    for c in chunks:
        if len(c):
            parts += [np.asarray(c, dtype=np.float32), gap]
    if not parts:
        raise RuntimeError("empty Thai audio")
    return to_pcm24k(np.concatenate(parts[:-1]), SR)


def synth_en(text: str) -> np.ndarray:
    body = json.dumps({"model": "kokoro", "input": text, "voice": kokoro_voice(),
                       "response_format": "wav", "speed": 1.0}).encode()
    req = urllib.request.Request(f"{KOKORO_URL}/v1/audio/speech", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    x, rate = read_wav(data)
    return to_pcm24k(x, rate)


# ---------------- DB ----------------
_db = None


def db():
    global _db
    if _db is None or _db.closed:
        _db = psycopg.connect(DATABASE_URL, autocommit=True)
    return _db


def save(lang: str, text: str, wav: bytes, duration_ms: int) -> str:
    for attempt in range(2):
        try:
            with db().cursor() as cur:
                cur.execute(
                    "INSERT INTO tts_audio (lang, text, wav, duration_ms) VALUES (%s,%s,%s,%s) RETURNING id",
                    (lang, text, wav, duration_ms),
                )
                return str(cur.fetchone()[0])
        except psycopg.OperationalError:
            global _db
            _db = None
            if attempt:
                raise


# ---------------- AMQP ----------------
def beat():
    try:
        HEARTBEAT_FILE.write_text(str(int(time.time())))
    except OSError:
        pass


def handle(ch, method, props, body):
    t0 = time.time()
    reply = {"type": "tts"}
    try:
        msg = json.loads(body or b"{}")
        text = clean_text(str(msg.get("text", "")))
        if not text:
            raise ValueError("empty text")
        lang = msg.get("lang") if msg.get("lang") in ("th", "en") else None
        lang = "th" if detect_lang(text) == "th" else (lang or "en")
        pcm = synth_th(text) if lang == "th" else synth_en(text)
        duration_ms = int(len(pcm) * 1000 / SR)
        audio_id = save(lang, text, wav_bytes(pcm), duration_ms)
        reply.update(audioId=audio_id, durationMs=duration_ms, lang=lang)
        log.info("ok %s lang=%s chars=%d dur=%dms took=%.2fs", audio_id, lang, len(text),
                 duration_ms, time.time() - t0)
    except Exception as e:
        log.exception("tts failed")
        reply["error"] = str(e)[:300]
    if props.reply_to:
        ch.basic_publish(
            exchange=REPLY_EXCHANGE, routing_key=props.reply_to, body=json.dumps(reply),
            properties=pika.BasicProperties(correlation_id=props.correlation_id,
                                            content_type="application/json"),
        )
    ch.basic_ack(method.delivery_tag)
    beat()


def run_once():
    params = pika.URLParameters(AMQP_URL)
    params.heartbeat = 120
    params.blocked_connection_timeout = 60
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.queue_declare(QUEUE, durable=True)
    ch.exchange_declare(REPLY_EXCHANGE, exchange_type="direct", durable=False)
    ch.basic_qos(prefetch_count=2)
    ch.basic_consume(QUEUE, handle)
    log.info("consuming %s (prefetch 2)", QUEUE)
    try:
        while True:
            conn.process_data_events(time_limit=5)
            beat()
    finally:
        try:
            conn.close()
        except Exception:
            pass


def main():
    while True:
        try:
            run_once()
        except KeyboardInterrupt:
            return
        except Exception as e:
            try:
                HEARTBEAT_FILE.unlink()
            except OSError:
                pass
            log.warning("AMQP disconnected (%s) - reconnect in 3s", e)
            time.sleep(3)


if __name__ == "__main__":
    main()
