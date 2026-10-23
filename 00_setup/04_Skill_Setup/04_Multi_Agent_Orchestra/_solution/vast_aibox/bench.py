"""bench.py — วัด ai-box จริง แล้วเขียนผลลง bench.json (รวมกับผลเดิมทีละหัวข้อ)

รันในอิมเมจเดียวกับ server (มี faster-whisper/numpy/soundfile ครบ):
  docker run --rm --gpus all -v aibox-hf:/hf -v <vast_aibox>:/src -v <samples>:/samples \
    -e AIBOX_URL=http://host.docker.internal:8090 -e AIBOX_API_KEY=... aibox:dev \
    python /src/bench.py --stage stt_acc,tts,rerank,conc,mixed --out /src/bench.json

stage:
  stt_acc   Whisper large-v3 vs large-v3-turbo (in-process) · FLEURS th_th test 25 คลิป CER + en_us 5 คลิป WER
  tts       VoxCPM2 ผ่าน API: ไทย 5 + อังกฤษ 5 ประโยค → RTF, time-to-audio, CER/WER ไป-กลับด้วย Whisper ของ server
  rerank    latency query + 20 passages
  conc      ความจุพร้อมกัน: STT (คลิปไทย 5 วิ, p95 ≤ 2 วิ) · TTS (1–3 ประโยค, p95 time-to-audio ≤ 4 วิ) · rerank req/s
  mixed     2 STT + 2 TTS + 2 rerank พร้อมกัน + peak VRAM (โพล /health ทุก 0.2 วิ)
  fixtures  ถอดเสียง e2e/voice-fixtures/*.wav แล้วคิด CER ต่อไฟล์

FLEURS: ดาวน์โหลดเฉพาะ test.tsv + audio/test.tar.gz ของ th_th และ en_us ไปที่ $FLEURS_DIR (ค่าเริ่มต้น /hf/fleurs)
"""
from __future__ import annotations

import argparse
import io
import json
import os
import random
import re
import statistics
import tarfile
import threading
import time
import unicodedata
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import soundfile as sf

URL = os.environ.get("AIBOX_URL", "http://localhost:8090").rstrip("/")
KEY = os.environ.get("AIBOX_API_KEY", "")
FLEURS_DIR = Path(os.environ.get("FLEURS_DIR", "/hf/fleurs"))
SAMPLES = Path(os.environ.get("SAMPLES_DIR", "/samples"))

TH_SENTS = [
    "สวัสดีครับ ยินดีต้อนรับสู่ร้านบ้านช่าง วันนี้กำลังมองหาวัสดุอะไรอยู่ครับ",
    "ปูนซีเมนต์ปอร์ตแลนด์ถุงละห้าสิบกิโลกรัม เก็บในที่แห้งได้ประมาณหกเดือนครับ",
    "ถ้าปูกระเบื้องหกสิบคูณหกสิบ แนะนำเกรียงหวีฟันสิบมิลลิเมตรครับ ปูนกาวจะได้เต็มแผ่น",
    "สาขารังสิตยังมีเหล็กข้ออ้อยอยู่ครับ ต้องการให้ผมใส่ตะกร้าไว้เลยไหมครับ",
    "สีทาภายนอกรุ่นนี้กันแดดกันฝนได้ดีมาก รับประกันห้าปีครับ ทาสองรอบก็สวยแล้ว",
]
EN_SENTS = [
    "Hello! Welcome to BuildMart. What are you building today?",
    "This exterior paint comes with a five year warranty. Two coats are usually enough.",
    "For sixty by sixty tiles, use a ten millimeter notched trowel.",
    "The Rangsit branch still has deformed steel bars in stock. Shall I add them to your cart?",
    "Portland cement should be stored in a dry place. It keeps for about six months.",
]


# ---------------------------------------------------------------- metrics
TH_DIG = ["ศูนย์", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]
TH_POS = ["", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน"]


def th_num(n: int) -> str:
    if n == 0:
        return TH_DIG[0]
    if n >= 1_000_000:
        return th_num(n // 1_000_000) + "ล้าน" + (th_num(n % 1_000_000) if n % 1_000_000 else "")
    ds, out = str(n)[::-1], ""
    for i, ch in enumerate(ds):
        d = int(ch)
        if d == 0:
            continue
        if i == 0 and d == 1 and len(ds) > 1:
            w = "เอ็ด"
        elif i == 1 and d == 2:
            w = "ยี่"
        elif i == 1 and d == 1:
            w = ""
        else:
            w = TH_DIG[d]
        out = w + TH_POS[i] + out
    return out


def spell_numbers(s: str, lang: str) -> str:
    """ตัวเลขอารบิก → คำอ่าน (Whisper มักเขียนเป็นตัวเลข ส่วนข้อความอ้างอิงสะกดเป็นคำ) · 60x60 → 60 คูณ/by 60"""
    s = re.sub(r"(?<=\d),(?=\d{3})", "", s)
    s = re.sub(r"(?<=\d)\s*[x×]\s*(?=\d)", " คูณ " if lang == "th" else " by ", s)
    if lang == "th":
        return re.sub(r"\d+", lambda m: th_num(int(m.group())), s)
    import inflect
    p = inflect.engine()
    return re.sub(r"\d+", lambda m: " " + p.number_to_words(int(m.group()), andword="").replace("-", " ") + " ", s)


def norm_chars(s: str) -> str:
    """CER: NFKC (ำ = ํ+า) · ตัดช่องว่าง/เครื่องหมายวรรคตอน/สัญลักษณ์ · เก็บสระ-วรรณยุกต์ไทย (category M)"""
    s = unicodedata.normalize("NFKC", s).lower()
    return "".join(c for c in s if unicodedata.category(c)[0] not in "PSZC")


def norm_words(s: str) -> list[str]:
    s = unicodedata.normalize("NFKC", s).lower()
    s = "".join(c if unicodedata.category(c)[0] not in "PS" or c == "'" else " " for c in s)
    return s.replace("'", "").split()


def lev(a, b) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def cer(hyp: str, ref: str, numbers: bool = True) -> float:
    if numbers:
        hyp, ref = spell_numbers(hyp, "th"), spell_numbers(ref, "th")
    r = norm_chars(ref)
    return lev(norm_chars(hyp), r) / max(1, len(r))


def wer(hyp: str, ref: str, numbers: bool = True) -> float:
    if numbers:
        hyp, ref = spell_numbers(hyp, "en"), spell_numbers(ref, "en")
    r = norm_words(ref)
    return lev(norm_words(hyp), r) / max(1, len(r))


def pct(xs, p):
    return float(np.percentile(np.asarray(xs, dtype=float), p)) if xs else None


def r3(x):
    return None if x is None else round(float(x), 3)


# ---------------------------------------------------------------- http
def _req(path: str, data: bytes | None = None, headers: dict | None = None, timeout=300):
    h = {"Authorization": f"Bearer {KEY}"}
    h.update(headers or {})
    # GPU แยก 2 เครื่อง: STT_URL / TTS_URL / RERANK_URL (ถ้ามี) ชนะ AIBOX_URL
    base = {"/v1/audio/transcriptions": os.environ.get("STT_URL"), "/v1/audio/speech": os.environ.get("TTS_URL"),
            "/v1/rerank": os.environ.get("RERANK_URL")}.get(path) or URL
    req = urllib.request.Request(base.rstrip("/") + path, data=data, headers=h, method="POST" if data is not None else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), dict(r.headers)


def health() -> dict:
    try:
        b, _ = _req("/health", timeout=10)
        return json.loads(b)
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def api_stt(wav_bytes: bytes, language: str | None = None, filename="a.wav") -> dict:
    boundary = uuid.uuid4().hex
    parts = []
    if language:
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="language"\r\n\r\n{language}\r\n'.encode())
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
                 f'Content-Type: application/octet-stream\r\n\r\n'.encode() + wav_bytes + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    b, _ = _req("/v1/audio/transcriptions", b"".join(parts), {"Content-Type": f"multipart/form-data; boundary={boundary}"})
    return json.loads(b)


def api_tts(text: str, voice="nongchang", **extra) -> tuple[bytes, dict]:
    body = json.dumps({"input": text, "voice": voice, "response_format": "wav", **extra}, ensure_ascii=False).encode()
    return _req("/v1/audio/speech", body, {"Content-Type": "application/json"})


def api_rerank(query: str, docs: list[str], top_n=None) -> dict:
    body = json.dumps({"query": query, "documents": docs, "top_n": top_n}, ensure_ascii=False).encode()
    b, _ = _req("/v1/rerank", body, {"Content-Type": "application/json"})
    return json.loads(b)


def wav_bytes(y: np.ndarray, sr=16000) -> bytes:
    buf = io.BytesIO()
    sf.write(buf, y, sr, format="WAV", subtype="PCM_16")
    return buf.getvalue()


# ---------------------------------------------------------------- FLEURS
def fleurs(lang: str, n: int, seed=0):
    """คืน [(id, audio float32 16k, transcript)] — ประโยคไม่ซ้ำ n ประโยคจาก test split"""
    tsv = FLEURS_DIR / f"data/{lang}/test.tsv"
    tar = FLEURS_DIR / f"data/{lang}/audio/test.tar.gz"
    if not tsv.exists() or not tar.exists():
        from huggingface_hub import hf_hub_download
        for f in (f"data/{lang}/test.tsv", f"data/{lang}/audio/test.tar.gz"):
            hf_hub_download("google/fleurs", f, repo_type="dataset", local_dir=str(FLEURS_DIR))
    rows, seen = [], set()
    for line in tsv.read_text(encoding="utf-8").splitlines():
        c = line.split("\t")
        if len(c) < 3 or c[0] in seen:
            continue
        seen.add(c[0])
        rows.append((c[0], c[1], c[2]))
    random.Random(seed).shuffle(rows)
    rows = rows[:n]
    want = {r[1]: r for r in rows}
    out = {}
    with tarfile.open(tar, "r:gz") as t:
        for m in t:
            name = m.name.split("/")[-1]
            if name in want and name not in out:
                y, sr = sf.read(io.BytesIO(t.extractfile(m).read()), dtype="float32")
                if y.ndim > 1:
                    y = y.mean(1)
                if sr != 16000:
                    import librosa
                    y = librosa.resample(y, orig_sr=sr, target_sr=16000)
                out[name] = y
                if len(out) == len(want):
                    break
    return [(r[0], out[r[1]], r[2]) for r in rows if r[1] in out]


# ---------------------------------------------------------------- stages
def stage_stt_acc(res: dict, n_th=25, n_en=5):
    from faster_whisper import WhisperModel
    import torch  # noqa: F401
    th, en = fleurs("th_th", n_th), fleurs("en_us", n_en)
    audio_s = sum(len(a) for _, a, _ in th) / 16000
    out = {"dataset": f"google/fleurs test · th_th {len(th)} clips ({audio_s:.0f} s audio) · en_us {len(en)} clips",
           "settings": "beam_size=5 condition_on_previous_text=False language fixed compression_ratio_threshold=3.3 (Thai)",
           "normalization": "NFKC, lowercase, strip whitespace/punctuation/symbols (Thai vowel & tone marks kept); "
                            "*_numnorm = digits spelled out on both sides before scoring",
           "models": {}}
    for name, ct in (("large-v3", "float16"), ("large-v3-turbo", "float16"), ("large-v3", "int8_float16"),
                     ("large-v3-turbo", "int8_float16")):
        m = WhisperModel(name, device="cuda", compute_type=ct)
        list(m.transcribe(np.zeros(16000, np.float32), language="th")[0])  # warm-up
        per, tot_e, tot_c, times = [], 0, 0, []
        for cid, a, ref in th:
            t0 = time.time()
            segs, _ = m.transcribe(a, language="th", beam_size=5, condition_on_previous_text=False,
                                   compression_ratio_threshold=3.3)
            hyp = "".join(s.text for s in segs).strip()
            dt = time.time() - t0
            times.append(dt)
            e = lev(norm_chars(spell_numbers(hyp, "th")), norm_chars(spell_numbers(ref, "th")))
            c = len(norm_chars(spell_numbers(ref, "th")))
            tot_e += e
            tot_c += c
            per.append({"id": cid, "dur_s": r3(len(a) / 16000), "sec": r3(dt), "cer": r3(e / c), "ref": ref, "hyp": hyp})
        en_w, en_n, en_t, en_per = 0, 0, [], []
        for cid, a, ref in en:
            t0 = time.time()
            segs, _ = m.transcribe(a, language="en", beam_size=5, condition_on_previous_text=False)
            hyp = "".join(s.text for s in segs).strip()
            en_t.append(time.time() - t0)
            e = lev(norm_words(spell_numbers(hyp, "en")), norm_words(spell_numbers(ref, "en")))
            c = len(norm_words(spell_numbers(ref, "en")))
            en_w += e
            en_n += c
            en_per.append({"id": cid, "wer": r3(e / c), "ref": ref, "hyp": hyp})
        out["models"][f"{name} {ct}"] = {
            "th_cer_corpus": r3(tot_e / tot_c), "th_cer_mean_clip": r3(statistics.mean(p["cer"] for p in per)),
            "th_sec_per_clip_mean": r3(statistics.mean(times)), "th_rtf": r3(sum(times) / audio_s),
            "en_wer_corpus": r3(en_w / en_n), "en_sec_per_clip_mean": r3(statistics.mean(en_t)),
            "th_clips": per, "en_clips": en_per}
        print(name, ct, {k: v for k, v in out["models"][f"{name} {ct}"].items() if not k.endswith("clips")}, flush=True)
        del m
    res["whisper_compare"] = out


def stage_stt_server(res: dict, n_th=25):
    """ถอด FLEURS ไทยผ่าน API จริง (ทาง micro-batch ของ server) ทีละคลิป และพร้อมกัน 8 คลิป"""
    th = fleurs("th_th", n_th)
    def score(hyps):
        e = c = 0
        for (cid, a, ref), hyp in zip(th, hyps):
            r = norm_chars(spell_numbers(ref, "th"))
            e += lev(norm_chars(spell_numbers(hyp, "th")), r)
            c += len(r)
        return r3(e / c)
    seq, ts = [], []
    for _, a, _ in th:
        t0 = time.time()
        seq.append(api_stt(wav_bytes(a), "th")["text"])
        ts.append(time.time() - t0)
    t0 = time.time()
    with ThreadPoolExecutor(8) as ex:
        par = list(ex.map(lambda x: api_stt(wav_bytes(x[1]), "th")["text"], th))
    wall = time.time() - t0
    auto = api_stt(wav_bytes(th[0][1]))
    h = health()
    res["stt_server"] = {"whisper_model": h.get("whisper_model"), "compute": h.get("whisper_compute"),
                         "clips": len(th), "cer_numnorm_sequential": score(seq), "cer_numnorm_parallel8": score(par),
                         "sec_per_clip_sequential": r3(statistics.mean(ts)), "wall_s_parallel8": r3(wall),
                         "auto_language_detect_clip0": auto.get("language"), "stt_batches": h.get("stt_batches")}
    print(res["stt_server"], flush=True)


def stage_tts(res: dict):
    SAMPLES.mkdir(parents=True, exist_ok=True)
    items = []
    for lang, sents in (("th", TH_SENTS), ("en", EN_SENTS)):
        for i, text in enumerate(sents, 1):
            t0 = time.time()
            b, h = api_tts(text, language=lang)
            tta = time.time() - t0
            y, sr = sf.read(io.BytesIO(b), dtype="float32")
            dur = len(y) / sr
            fn = SAMPLES / f"tts_{lang}{i}.wav"
            fn.write_bytes(b)
            tr = api_stt(b, language=lang)
            m = cer(tr["text"], text) if lang == "th" else wer(tr["text"], text)
            m_raw = cer(tr["text"], text, False) if lang == "th" else wer(tr["text"], text, False)
            rms = float(np.sqrt((y ** 2).mean()))
            items.append({"lang": lang, "text": text, "audio_s": r3(dur), "time_to_audio_s": r3(tta),
                          "gen_s": r3(float(h.get("X-Gen-Seconds", h.get("x-gen-seconds", 0)))),
                          "rtf": r3(tta / dur), "rms": round(rms, 4), "peak": r3(np.abs(y).max()),
                          "chars_per_s": r3(len(norm_chars(text)) / dur),
                          ("cer" if lang == "th" else "wer"): r3(m),
                          ("cer_raw" if lang == "th" else "wer_raw"): r3(m_raw), "whisper": tr["text"], "file": str(fn.name),
                          "sane": bool(0.02 < rms < 0.3 and 0.8 < dur < 30)})
            print(lang, i, items[-1]["audio_s"], items[-1]["time_to_audio_s"], items[-1]["rtf"], r3(m), tr["text"], flush=True)

    def agg(lang, key):
        xs = [x[key] for x in items if x["lang"] == lang]
        return r3(statistics.mean(xs))
    res["tts"] = {"engine": "VoxCPM2 (openbmb/VoxCPM2, bf16, torch.compile, 10 diffusion steps, cfg 2.0)",
                  "voice": "nongchang (clone: reference + continuation from voices/nongchang.wav)",
                  "summary": {l: {"rtf_mean": agg(l, "rtf"), "time_to_audio_mean_s": agg(l, "time_to_audio_s"),
                                  "audio_s_mean": agg(l, "audio_s"),
                                  ("cer_mean" if l == "th" else "wer_mean"): agg(l, "cer" if l == "th" else "wer")}
                              for l in ("th", "en")},
                  "items": items}


PASSAGES = [
    "ปูนซีเมนต์ปอร์ตแลนด์ประเภท 1 ถุง 50 กก. ควรเก็บในที่แห้ง ยกพื้นสูงจากพื้น 10 ซม. ไม่ควรเก็บนานเกิน 6 เดือน",
    "กระเบื้องขนาด 60x60 ซม. ขึ้นไป ให้ใช้เกรียงหวีฟัน 10 มม. และป้ายปูนกาวทั้งพื้นและหลังแผ่น",
    "ปูนกาวซีเมนต์สำหรับกระเบื้อง อัตราการใช้ 4–6 กก./ตร.ม. ขึ้นกับขนาดฟันเกรียง",
    "เหล็กข้ออ้อย DB12 SD40 ยาว 10 เมตร น้ำหนัก 8.88 กก./เส้น ตาม มอก. 24-2559",
    "สายไฟ THW ขนาด 2.5 ตร.มม. ใช้คู่เบรกเกอร์ 16–20 แอมป์ สำหรับวงจรเต้ารับ",
    "สีทาภายนอกอะคริลิก 100% รับประกันการหลุดลอก 5 ปี ทา 2 เที่ยว เว้น 2 ชั่วโมง",
    "นโยบายคืนสินค้า: คืนได้ภายใน 7 วัน สินค้าต้องอยู่ในสภาพเดิม พร้อมใบเสร็จ",
    "ค่าจัดส่งในรัศมี 10 กม. คิดตามน้ำหนัก รถกระบะรับได้ไม่เกิน 1.5 ตัน",
    "ท่อ PVC ชั้น 8.5 สำหรับน้ำประปา ท่อชั้น 13.5 สำหรับงานแรงดันสูง",
    "รองพื้นปูนใหม่ต้องรอปูนแห้งอย่างน้อย 28 วัน หรือใช้รองพื้นกันด่าง",
    "The exterior acrylic paint carries a 5-year warranty against peeling.",
    "Tile adhesive coverage is 4 to 6 kg per square metre depending on trowel notch size.",
    "เหล็กเส้นกลม RB9 ใช้ทำปลอกเสา ระยะห่าง 15–20 ซม.",
    "การผสมคอนกรีตอัตราส่วน 1:2:4 ใช้กับงานพื้นและคานทั่วไป",
    "ลูกค้าสมาชิกได้ส่วนลด 5% เมื่อซื้อครบ 5,000 บาท",
    "ปูนฉาบสำเร็จรูปใช้น้ำ 8–9 ลิตรต่อถุง 50 กก.",
    "กระเบื้องแกรนิตโต้ดูดซึมน้ำน้อยกว่า 0.5% เหมาะกับพื้นภายนอก",
    "เบรกเกอร์ลูกย่อย 32 แอมป์ ใช้กับสายไฟ 6 ตร.มม. สำหรับเครื่องทำน้ำอุ่น",
    "สีน้ำมันสำหรับงานเหล็ก ควรทารองพื้นกันสนิมก่อน 1 เที่ยว",
    "ใบเสนอราคามีอายุ 30 วัน นับจากวันที่ออกเอกสาร",
]
QUERIES = ["ปูกระเบื้องหกสิบคูณหกสิบ ใช้เกรียงฟันกี่มิล", "สีทาภายนอกรับประกันกี่ปี",
           "สายไฟ 2.5 ใช้เบรกเกอร์กี่แอมป์", "ปูนเก็บได้นานแค่ไหน", "How much tile adhesive per square metre?"]
EXPECT = [1, 5, 4, 0, 11]


def stage_rerank(res: dict):
    api_rerank("warm", PASSAGES)
    lat, hits = [], 0
    for _ in range(4):
        for q, exp in zip(QUERIES, EXPECT):
            t0 = time.time()
            r = api_rerank(q, PASSAGES, top_n=4)
            lat.append(time.time() - t0)
        if _ == 0:
            pass
    for q, exp in zip(QUERIES, EXPECT):
        top = [x["index"] for x in api_rerank(q, PASSAGES, top_n=4)["results"]]
        hits += exp == top[0]
    res["rerank"] = {"model": "BAAI/bge-reranker-v2-m3 fp16 max_len 512", "passages": len(PASSAGES),
                     "requests": len(lat), "latency_p50_s": r3(pct(lat, 50)), "latency_p95_s": r3(pct(lat, 95)),
                     "latency_mean_s": r3(statistics.mean(lat)), "top1_correct": f"{hits}/{len(QUERIES)}"}
    print(res["rerank"], flush=True)


def load_level(fn, conc: int, per_worker: int):
    lat, errs = [], 0
    lock = threading.Lock()

    def worker(w):
        nonlocal errs
        for k in range(per_worker):
            t0 = time.time()
            try:
                fn(w, k)
                with lock:
                    lat.append(time.time() - t0)
            except Exception as e:  # noqa: BLE001
                with lock:
                    errs += 1
                print("ERR", type(e).__name__, e, flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(conc) as ex:
        list(ex.map(worker, range(conc)))
    wall = time.time() - t0
    return {"concurrency": conc, "requests": len(lat), "errors": errs, "p50_s": r3(pct(lat, 50)),
            "p95_s": r3(pct(lat, 95)), "max_s": r3(max(lat) if lat else None), "wall_s": r3(wall),
            "throughput_rps": r3(len(lat) / wall)}


def stage_conc(res: dict, stt_levels=(1, 2, 4, 6, 8, 12, 16), tts_levels=(1, 2, 3, 4, 6), rr_levels=(1, 4, 8, 16)):
    out = {"note": "closed-loop: N clients each send requests back-to-back; latency = request → full response"}
    # STT: คลิปไทย FLEURS ตัดเหลือ 5.0 วิ
    clips = [wav_bytes(a[:80000]) for _, a, _ in fleurs("th_th", 12, seed=7) if len(a) >= 80000][:8]
    api_stt(clips[0], "th")
    stt = []
    for c in stt_levels:
        r = load_level(lambda w, k: api_stt(clips[(w + k) % len(clips)], "th"), c, max(3, 24 // c))
        stt.append(r)
        print("stt", r, flush=True)
    ok = [r["concurrency"] for r in stt if r["p95_s"] is not None and r["p95_s"] <= 2.0 and not r["errors"]]
    out["stt"] = {"clip": "Thai FLEURS 5.0 s, language=th, beam 5", "target": "p95 <= 2.0 s",
                  "max_concurrency_within_target": max(ok) if ok else 0, "levels": stt,
                  "audio_seconds_per_wall_second_at_max": None}
    if ok:
        best = [r for r in stt if r["concurrency"] == max(ok)][0]
        out["stt"]["audio_seconds_per_wall_second_at_max"] = r3(best["throughput_rps"] * 5.0)
    # TTS: 1–3 ประโยค (ไทย)
    tts = []
    for c in tts_levels:
        r = load_level(lambda w, k: api_tts(TH_SENTS[(w + k) % len(TH_SENTS)]), c, max(2, 8 // c))
        tts.append(r)
        print("tts", r, flush=True)
    ok = [r["concurrency"] for r in tts if r["p95_s"] is not None and r["p95_s"] <= 4.0 and not r["errors"]]
    out["tts"] = {"text": "Thai shop-assistant 1–2 sentences (~5–7 s audio)", "target": "p95 time-to-audio <= 4.0 s",
                  "max_concurrency_within_target": max(ok) if ok else 0, "levels": tts,
                  "note": "VoxCPM2 runs one request at a time (CUDA graphs) → extra requests queue"}
    # rerank
    rr = []
    for c in rr_levels:
        r = load_level(lambda w, k: api_rerank(QUERIES[(w + k) % len(QUERIES)], PASSAGES, 4), c, max(5, 40 // c))
        rr.append(r)
        print("rerank", r, flush=True)
    out["rerank"] = {"payload": "query + 20 passages, top_n 4", "levels": rr,
                     "max_throughput_rps": max(r["throughput_rps"] for r in rr)}
    res["concurrency"] = out


def stage_mixed(res: dict):
    clips = [wav_bytes(a[:80000]) for _, a, _ in fleurs("th_th", 6, seed=3) if len(a) >= 80000][:2]
    peak = {"vram_mb": 0}
    stop = threading.Event()
    before = health()

    def poll():
        while not stop.is_set():
            h = health()
            peak["vram_mb"] = max(peak["vram_mb"], h.get("vram_mb", 0))
            peak["torch_max_reserved_mb"] = h.get("torch_max_reserved_mb")
            time.sleep(0.2)
    th = threading.Thread(target=poll)
    th.start()
    jobs = [lambda: api_stt(clips[0], "th"), lambda: api_stt(clips[1], "th"),
            lambda: api_tts(TH_SENTS[2]), lambda: api_tts(EN_SENTS[1]),
            lambda: api_rerank(QUERIES[0], PASSAGES, 4), lambda: api_rerank(QUERIES[1], PASSAGES, 4)]
    names = ["stt", "stt", "tts", "tts", "rerank", "rerank"]
    lat = {}

    def run(i):
        t0 = time.time()
        jobs[i]()
        lat.setdefault(names[i], []).append(r3(time.time() - t0))
    for _ in range(3):
        with ThreadPoolExecutor(6) as ex:
            list(ex.map(run, range(6)))
    stop.set()
    th.join()
    res["mixed"] = {"load": "2 STT + 2 TTS + 2 rerank concurrently × 3 rounds", "latency_s": lat,
                    "gpu_used_before_mb": before.get("vram_mb"), "gpu_used_peak_mb": peak["vram_mb"],
                    "torch_max_reserved_mb": peak.get("torch_max_reserved_mb")}
    print(res["mixed"], flush=True)


def stage_fixtures(res: dict, fixdir: Path):
    qs = json.loads((fixdir / "questions.json").read_text(encoding="utf-8"))
    out = []
    for q in qs:
        b = (fixdir / f"{q['id']}.wav").read_bytes()
        t0 = time.time()
        tr = api_stt(b, q.get("lang"))
        m = cer(tr["text"], q["text"])
        out.append({"id": q["id"], "lang": q.get("lang"), "text": q["text"], "whisper": tr["text"],
                    "cer": r3(m), "sec": r3(time.time() - t0)})
        print(out[-1], flush=True)
    h = health()
    res["fixtures_stt"] = {"whisper_model": h.get("whisper_model"), "items": out,
                           "cer_mean": r3(statistics.mean(x["cer"] for x in out))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="stt_acc,tts,rerank,conc,mixed")
    ap.add_argument("--out", default=str(Path(__file__).with_name("bench.json")))
    ap.add_argument("--fixtures", default="/fixtures")
    a = ap.parse_args()
    outp = Path(a.out)
    res = json.loads(outp.read_text(encoding="utf-8")) if outp.exists() else {}
    for st in a.stage.split(","):
        t0 = time.time()
        if st == "fixtures":
            stage_fixtures(res, Path(a.fixtures))
        else:
            globals()[f"stage_{st}"](res)
        print(f"== {st} done in {time.time() - t0:.0f}s", flush=True)
        h = health()
        res.setdefault("env", {}).update({"gpu": h.get("gpu"), "measured_at": time.strftime("%Y-%m-%d %H:%M"),
                                          "server_whisper_model": h.get("whisper_model")})
        outp.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
