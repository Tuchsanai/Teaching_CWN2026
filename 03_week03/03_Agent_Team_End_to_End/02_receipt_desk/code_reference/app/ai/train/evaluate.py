#!/usr/bin/env python3
"""ReceiptDesk model gate: measure NFR-01 M1–M6 (+ M7 report-only) on the Test Set.

The flags come from the SAME rules the web uses (receipt_common == web/lib/rules.ts):
  BR-04  total_confidence < 0.90 (no rounding)              -> "ไม่แน่ใจยอดรวม"
  BR-05  |sum(item prices) - total| > 1.00 baht (in satang) -> "ยอดไม่ตรงรายการ"
Routing mirrors production (DESIGN 6.3): an answer that is not a full 5-field JSON (or says
{"unreadable": true}) is a failed read and ends in the "อ่านไม่ได้" pile, where a person types it in.

  M1 Total Accuracy   = receipts whose total (2 dp) == truth            / N        >= 95.0 %
  M2 Silent Error     = total wrong AND not flagged AND not in the pile / N        <=  1.0 %
  M3 Flag Recall      = total wrong AND (flagged or pile)            / wrong      >= 80.0 %
  M4 Flag Rate        = flagged or pile                              / N        <= 20.0 %
  M5 Abstention       = unreadable set: total answered without a flag (count)    ==  0
  M6 JSON Validity    = full 5-field structure                       / N        >= 99.0 %
  M7 Item F1          = item-name F1, 1–2 typos tolerated (report only)
N = readable Test Set (>= 200 receipts); unreadable set >= 20 receipts. A model is deployable only
when M1–M6 all pass (exit code 0). Exit 1 = gate failed, 2 = incomplete run (infra errors / bad input).

Backends
  --backend vllm         OpenAI-compatible vLLM/NGINX endpoint (what the GPU worker calls), logprobs on
  --backend hf           local transformers model (+ optional --adapter from train_lora.py)
  --backend predictions  score an existing JSONL: {"id", "output": <raw text>, "total_confidence"}

  --dry-run              CPU only, no GPU/model download: self-test the rules against TEST-DATA BR-04/05
                         and the NFR-01 boundary examples, then run the whole pipeline on 200+20 synthetic
                         receipts with a scripted model whose expected counts are known. With
                         --backend vllm it also starts a local fake vLLM server (tests the HTTP client and
                         logprob->confidence code); with --backend hf it runs a tiny random VLM.
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures as cf
import hashlib
import io
import json
import logging
import math
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import receipt_common as rc  # noqa: E402

LOG = logging.getLogger("evaluate")
MIN_READABLE, MIN_UNREADABLE = 200, 20


# ----------------------------------------------------------------------------------------------
# Metric gate (exact integer arithmetic so 95/100 is exactly 95.0 %)
# ----------------------------------------------------------------------------------------------
@dataclass
class Counts:
    n: int = 0  # readable receipts
    correct: int = 0
    wrong: int = 0
    silent: int = 0
    caught: int = 0
    needs_review: int = 0  # flagged or pile
    flagged_only: int = 0  # valid & flagged (excludes pile) — informational
    valid: int = 0
    n_unreadable: int = 0
    m5_violations: int = 0
    item_tp: int = 0
    item_pred: int = 0
    item_gold: int = 0


def gate(c: Counts) -> list[dict[str, Any]]:
    def pct(num: int, den: int) -> float | None:
        return None if den == 0 else round(100.0 * num / den, 2)

    def ratio(num: int, den: int) -> Fraction:
        return Fraction(num, den) if den else Fraction(0)

    m3_ok = c.wrong == 0 or ratio(c.caught, c.wrong) >= Fraction(80, 100)
    p = Fraction(c.item_tp, c.item_pred) if c.item_pred else Fraction(0)
    r = Fraction(c.item_tp, c.item_gold) if c.item_gold else Fraction(0)
    f1 = float(2 * p * r / (p + r)) if (p + r) else 0.0
    return [
        dict(id="M1", name="Total Accuracy", num=c.correct, den=c.n, value=pct(c.correct, c.n), rule=">= 95.0%",
             passed=c.n > 0 and ratio(c.correct, c.n) >= Fraction(95, 100)),
        dict(id="M2", name="Silent Error Rate", num=c.silent, den=c.n, value=pct(c.silent, c.n), rule="<= 1.0%",
             passed=c.n > 0 and ratio(c.silent, c.n) <= Fraction(1, 100)),
        dict(id="M3", name="Flag Recall", num=c.caught, den=c.wrong,
             value=pct(c.caught, c.wrong) if c.wrong else 100.0, rule=">= 80.0% (no wrong totals = pass)",
             passed=c.n > 0 and m3_ok),
        dict(id="M4", name="Flag Rate", num=c.needs_review, den=c.n, value=pct(c.needs_review, c.n),
             rule="<= 20.0%", passed=c.n > 0 and ratio(c.needs_review, c.n) <= Fraction(20, 100)),
        dict(id="M5", name="Abstention (unreadable set)", num=c.m5_violations, den=c.n_unreadable,
             value=c.m5_violations, rule="== 0 receipts", passed=c.n_unreadable > 0 and c.m5_violations == 0),
        dict(id="M6", name="JSON Validity", num=c.valid, den=c.n, value=pct(c.valid, c.n), rule=">= 99.0%",
             passed=c.n > 0 and ratio(c.valid, c.n) >= Fraction(99, 100)),
        dict(id="M7", name="Item F1 (report only)", num=c.item_tp, den=c.item_gold, value=round(100 * f1, 2),
             rule="not a gate", passed=None),
    ]


# ----------------------------------------------------------------------------------------------
# Scoring one receipt
# ----------------------------------------------------------------------------------------------
@dataclass
class Prediction:
    id: str
    output: str | None  # raw model text (None = no answer: timeout / HTTP error)
    total_confidence: float | None
    attempts: int = 1
    infra_error: str | None = None
    latency_s: float | None = None


def score(rows: list[dict[str, Any]], preds: dict[str, Prediction],
          threshold: Decimal = rc.CONFIDENCE_THRESHOLD) -> tuple[Counts, list[dict[str, Any]]]:
    c, detail = Counts(), []
    for row in rows:
        pred = preds.get(row["id"])
        parsed = rc.parse_model_output(pred.output if pred else None)
        conf = pred.total_confidence if pred else None
        in_pile = not parsed.valid  # failed read -> "อ่านไม่ได้" pile (DESIGN 6.3)
        low, mismatch = rc.flags_for(parsed, conf, threshold) if parsed.valid else (False, False)
        flagged = low or mismatch
        d = {"id": row["id"], "set": "unreadable" if row["unreadable"] else "readable", "valid": parsed.valid,
             "model_unreadable": parsed.unreadable, "flag_low_confidence": low, "flag_mismatch": mismatch,
             "pile": in_pile, "error": parsed.error, "total_confidence": conf}
        if row["unreadable"]:
            c.n_unreadable += 1
            violation = parsed.valid and not flagged  # answered a total without saying "not sure"
            c.m5_violations += violation
            d["m5_violation"] = violation
        else:
            c.n += 1
            gold_total = rc.parse_amount_satang(row["total"])
            correct = parsed.valid and parsed.total_satang == gold_total
            review = in_pile or flagged
            c.correct += correct
            c.wrong += not correct
            c.silent += (not correct) and not review
            c.caught += (not correct) and review
            c.needs_review += review
            c.flagged_only += parsed.valid and flagged
            c.valid += parsed.valid
            gold_names = [str(it["name"]) for it in row["items"]]
            pred_names = [it["name"] for it in parsed.items] if parsed.valid else []
            c.item_tp += rc.item_name_matches(pred_names, gold_names)
            c.item_pred += len(pred_names)
            c.item_gold += len(gold_names)
            d.update(total_correct=correct, silent_error=(not correct) and not review)
        detail.append(d)
    return c, detail


# ----------------------------------------------------------------------------------------------
# Backends
# ----------------------------------------------------------------------------------------------
def encode_png(img) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class VLLMClient:
    """Same request the GPU worker sends: OpenAI chat completions + image + logprobs."""

    def __init__(self, url: str, model: str, api_key: str | None, timeout: float, max_tokens: int,
                 image_max_side: int):
        self.url = url.rstrip("/") + "/v1/chat/completions"
        self.model, self.api_key, self.timeout = model, api_key, timeout
        self.max_tokens, self.image_max_side = max_tokens, image_max_side

    def payload(self, png: bytes) -> dict[str, Any]:
        data_url = "data:image/png;base64," + base64.b64encode(png).decode()
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": rc.SYSTEM_PROMPT},
                {"role": "user", "content": [{"type": "image_url", "image_url": {"url": data_url}},
                                             {"type": "text", "text": rc.USER_PROMPT}]},
            ],
            "temperature": 0,
            "max_tokens": self.max_tokens,
            "logprobs": True,
        }

    def __call__(self, row: dict[str, Any]) -> tuple[str, float | None]:
        png = encode_png(rc.load_image(row["image"], self.image_max_side))
        req = urllib.request.Request(self.url, data=json.dumps(self.payload(png)).encode(), method="POST",
                                     headers={"Content-Type": "application/json"})
        if self.api_key:
            req.add_header("Authorization", f"Bearer {self.api_key}")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            body = json.loads(resp.read())
        choice = body["choices"][0]
        text = choice["message"]["content"] or ""
        pieces = []
        for tok in ((choice.get("logprobs") or {}).get("content") or []):
            piece = bytes(tok["bytes"]) if tok.get("bytes") is not None else tok["token"]
            pieces.append((piece, float(tok["logprob"])))
        return text, rc.confidence_from_token_spans(text, rc.spans_from_token_pieces(pieces))


class HFPredictor:
    """Local transformers inference (base model + optional LoRA adapter); confidence from scores."""

    def __init__(self, model: str, adapter: str | None, image_max_side: int, max_tokens: int,
                 precision: str = "auto", attn: str = "sdpa"):
        import torch
        from train_lora import load_base_model, load_processor, resolve_dtype

        ns = argparse.Namespace(attn_implementation=attn, load_in_4bit=False,
                                min_pixels=256 * 28 * 28, max_pixels=1280 * 28 * 28)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = load_processor(adapter or model, ns)
        self.processor.tokenizer.padding_side = "left"
        m = load_base_model(model, ns, resolve_dtype(precision), 0, for_training=False)
        if adapter:
            from peft import PeftModel

            m = PeftModel.from_pretrained(m, adapter)
        self.model = m.to(self.device).eval()
        self.prompt = self.processor.apply_chat_template(rc.build_messages(), tokenize=False,
                                                         add_generation_prompt=True)
        self.image_max_side, self.max_tokens = image_max_side, max_tokens
        self.lock = threading.Lock()

    def __call__(self, row: dict[str, Any]) -> tuple[str, float | None]:
        import torch

        tok = self.processor.tokenizer
        enc = self.processor(text=[self.prompt], images=[rc.load_image(row["image"], self.image_max_side)],
                             return_tensors="pt").to(self.device)
        with self.lock, torch.no_grad():
            out = self.model.generate(**enc, max_new_tokens=self.max_tokens, do_sample=False,
                                      output_scores=True, return_dict_in_generate=True)
            scores = self.model.compute_transition_scores(out.sequences, out.scores, normalize_logits=True)[0]
        ids = out.sequences[0, enc["input_ids"].shape[1]:].tolist()
        stop = {tok.eos_token_id, tok.pad_token_id} - {None}
        n = next((i for i, t in enumerate(ids) if t in stop), len(ids))
        spans, prev = [], ""
        for i in range(n):
            cur = tok.decode(ids[: i + 1], skip_special_tokens=True)
            spans.append((len(prev), len(cur), float(scores[i])))
            prev = cur
        text = tok.decode(ids[:n], skip_special_tokens=True)
        return text, rc.confidence_from_token_spans(text, spans)


def run_predictor(rows: list[dict[str, Any]], fn: Callable[[dict[str, Any]], tuple[str, float | None]],
                  attempts: int, concurrency: int) -> dict[str, Prediction]:
    """Call the model per receipt. attempts>1 re-asks after an invalid answer, like BR-07 (max 3)."""

    def one(row: dict[str, Any]) -> Prediction:
        last = Prediction(row["id"], None, None, 0)
        for k in range(1, attempts + 1):
            t0 = time.time()
            try:
                text, conf = fn(row)
                last = Prediction(row["id"], text, conf, k, None, round(time.time() - t0, 3))
                if rc.parse_model_output(text).valid:
                    break
            except (urllib.error.URLError, TimeoutError, OSError, KeyError, ValueError) as exc:
                last = Prediction(row["id"], None, None, k, f"{type(exc).__name__}: {exc}"[:200])
        return last

    out: dict[str, Prediction] = {}
    with cf.ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        for i, pred in enumerate(pool.map(one, rows), 1):
            out[pred.id] = pred
            if i % 25 == 0 or i == len(rows):
                LOG.info("predicted %d/%d", i, len(rows))
    return out


def load_predictions(path: str) -> dict[str, Prediction]:
    preds = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        output = d.get("output")
        if output is None and isinstance(d.get("result"), dict):  # gateway-style result object
            output = json.dumps(d["result"], ensure_ascii=False)
            d.setdefault("total_confidence", d["result"].get("total_confidence"))
        preds[d["id"]] = Prediction(d["id"], output, d.get("total_confidence"), d.get("attempts", 1),
                                    d.get("infra_error"))
    return preds


# ----------------------------------------------------------------------------------------------
# Dry-run: rule self-test, scripted model with known answers, fake vLLM server
# ----------------------------------------------------------------------------------------------
def self_test() -> list[str]:
    """Return failures (empty = OK). Cases are TEST-DATA BR-04 / BR-05 and NFR-01 examples verbatim."""
    fails: list[str] = []
    s = rc.parse_amount_satang
    items100 = [s("45.00"), s("30.00"), s("25.00")]
    br04 = [("TD-BR04-a", "0.89", items100, True), ("TD-BR04-b", "0.90", items100, False),
            ("TD-BR04-c", "0.91", items100, False), ("TD-BR04-d", "0.8999", items100, True),
            ("TD-BR04-b(float)", 0.9, items100, False)]
    for case, conf, items, want in br04:
        got = rc.flag_low_confidence(conf)
        if got != want or rc.flag_mismatch(items, s("100.00")):
            fails.append(f"{case}: low_conf={got} want {want}")
    low, mis = rc.flag_low_confidence("0.50"), rc.flag_mismatch([s("95.00")], s("100.00"))
    if not (low and mis):
        fails.append("TD-BR04-e both-flags: expected both flags")
    br05 = [("TD-BR05-a", ["45.00", "30.00", "24.01"], False), ("TD-BR05-b", ["45.00", "30.00", "24.00"], False),
            ("TD-BR05-c", ["45.00", "30.00", "23.99"], True), ("TD-BR05-d", ["60.00", "41.01"], True),
            ("TD-BR05-e", ["50.00", "48.51"], True)]
    for case, prices, want in br05:
        got = rc.flag_mismatch([s(p) for p in prices], s("100.00"))
        if got != want or rc.flag_low_confidence("0.99"):
            fails.append(f"{case}: mismatch={got} want {want}")

    def gate_of(**kw) -> dict[str, bool]:
        base = dict(n=100, correct=100, wrong=0, silent=0, caught=0, needs_review=0, valid=100,
                    n_unreadable=20, m5_violations=0)
        base.update(kw)
        return {m["id"]: m["passed"] for m in gate(Counts(**base))}

    nfr = [("M1", dict(correct=94, wrong=6, caught=6, needs_review=6), False),
           ("M1", dict(correct=95, wrong=5, caught=5, needs_review=5), True),
           ("M1", dict(correct=96, wrong=4, caught=4, needs_review=4), True),
           ("M2", dict(correct=96, wrong=4, silent=0, caught=4, needs_review=4), True),
           ("M2", dict(correct=96, wrong=4, silent=1, caught=3, needs_review=3), True),
           ("M2", dict(correct=96, wrong=4, silent=2, caught=2, needs_review=2), False),
           ("M3", dict(correct=95, wrong=5, caught=3, silent=2, needs_review=3), False),
           ("M3", dict(correct=95, wrong=5, caught=4, silent=1, needs_review=4), True),
           ("M3", dict(correct=95, wrong=5, caught=5, silent=0, needs_review=5), True),
           ("M4", dict(needs_review=19), True), ("M4", dict(needs_review=20), True),
           ("M4", dict(needs_review=21), False),
           ("M5", dict(m5_violations=0), True), ("M5", dict(m5_violations=1), False),
           ("M6", dict(valid=98), False), ("M6", dict(valid=99), True)]
    for metric, kw, want in nfr:
        got = gate_of(**kw)[metric]
        if got != want:
            fails.append(f"NFR-01 example {metric} {kw}: passed={got} want {want}")
    parsed = rc.parse_model_output('```json\n{"merchant":"ร้านตัวอย่าง","date":"2026-11-18","items":'
                                   '[{"name":"ข้าวสาร 5 กก.","price":"45.00"}],"total":"100.00"}\n```')
    if not (parsed.valid and parsed.total_satang == 10000):
        fails.append("parser: fenced Thai JSON not accepted")
    if rc.parse_model_output('{"merchant":"x","date":"2026-02-30","items":[],"total":"1.00"}').valid:
        fails.append("parser: invalid calendar date accepted")
    if not rc.parse_model_output('{"unreadable": true}').unreadable:
        fails.append("parser: unreadable answer not recognised")
    return fails


def scripted_outputs(rows: list[dict[str, Any]]) -> tuple[dict[str, tuple[str, float]], Counts]:
    """A fake model with a known error mix; returns {id: (raw text, confidence)} and expected counts."""
    def as_text(row, total=None, items=None):
        obj = {"merchant": row["merchant"], "date": row["date"],
               "items": items if items is not None else row["items"], "total": total or row["total"]}
        return json.dumps(obj, ensure_ascii=False)

    def shift(amount: str, satang: int) -> str:
        return rc.satang_to_str(rc.parse_amount_satang(amount) + satang)

    out: dict[str, tuple[str, float]] = {}
    readable = [r for r in rows if not r["unreadable"]]
    unreadable = [r for r in rows if r["unreadable"]]
    for i, row in enumerate(readable):
        if i < 4:  # wrong total, low confidence (and off by 12.00 vs items) -> caught
            out[row["id"]] = (as_text(row, shift(row["total"], 1200)), 0.60)
        elif i < 7:  # wrong total, confident, items disagree by 10.00 -> BR-05 catches it
            out[row["id"]] = (as_text(row, shift(row["total"], 1000)), 0.95)
        elif i == 7:  # wrong by 0.50, confident, within 1.00 of items -> SILENT error
            out[row["id"]] = (as_text(row, shift(row["total"], 50)), 0.95)
        elif i == 8:  # truncated JSON -> invalid -> pile
            out[row["id"]] = (as_text(row)[:25], 0.95)
        elif i == 9:  # correct but unsure -> false alarm flag
            out[row["id"]] = (as_text(row), 0.85)
        elif i == 10:  # correct, first item price off by exactly 1.00 -> BR-05 boundary, no flag
            items = [dict(it) for it in row["items"]]
            items[0]["price"] = shift(items[0]["price"], 100)
            out[row["id"]] = (as_text(row, items=items), 0.97)
        else:
            out[row["id"]] = (as_text(row), 0.97)
    for j, row in enumerate(unreadable):
        if j == len(unreadable) - 2:  # answers a total but flags it (conf 0.40) -> allowed
            out[row["id"]] = (json.dumps({"merchant": "?", "date": "2026-11-01", "items": [],
                                          "total": "120.00"}), 0.40)
        elif j == len(unreadable) - 1:
            out[row["id"]] = ("Sorry, I cannot read this receipt.", 0.10)
        else:
            out[row["id"]] = ('{"unreadable": true}', 0.99)
    n = len(readable)
    gold_items = sum(len(r["items"]) for r in readable)
    pred_items = gold_items - len(readable[8]["items"])
    expected = Counts(n=n, correct=n - 9, wrong=9, silent=1, caught=8, needs_review=9, flagged_only=8,
                      valid=n - 1, n_unreadable=len(unreadable), m5_violations=0,
                      item_tp=pred_items, item_pred=pred_items, item_gold=gold_items)
    return out, expected


def start_fake_vllm(rows: list[dict[str, Any]], scripted: dict[str, tuple[str, float]], image_max_side: int):
    """Local OpenAI-compatible server that answers like vLLM, incl. per-token logprobs with UTF-8 bytes."""
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    by_image = {hashlib.sha256(encode_png(rc.load_image(r["image"], image_max_side))).hexdigest(): r["id"]
                for r in rows}

    def tokens_for(text: str, conf: float) -> list[dict[str, Any]]:
        raw = text.encode("utf-8")
        chunks = [raw[i:i + 3] for i in range(0, len(raw), 3)]  # 3-byte chunks split Thai chars on purpose
        spans = rc.spans_from_token_pieces([(c, 0.0) for c in chunks])
        value = rc.total_value_span(text)
        hit = [k for k, (a, b, _) in enumerate(spans) if value and a < value[1] and b > value[0]]
        lp = math.log(conf) / len(hit) if hit else 0.0
        return [{"token": c.decode("utf-8", errors="replace"), "bytes": list(c),
                 "logprob": lp if k in hit else 0.0} for k, c in enumerate(chunks)]

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):  # quiet
            pass

        def do_POST(self):
            req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            url = req["messages"][1]["content"][0]["image_url"]["url"]
            rid = by_image.get(hashlib.sha256(base64.b64decode(url.split(",", 1)[1])).hexdigest())
            text, conf = scripted[rid]
            body = {"id": "fake", "object": "chat.completion", "model": req["model"],
                    "choices": [{"index": 0, "message": {"role": "assistant", "content": text},
                                 "logprobs": {"content": tokens_for(text, conf) if req.get("logprobs") else None},
                                 "finish_reason": "stop"}]}
            data = json.dumps(body).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


# ----------------------------------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------------------------------
def write_report(out_dir: Path, metrics: list[dict[str, Any]], counts: Counts, detail: list[dict[str, Any]],
                 preds: dict[str, Prediction], meta: dict[str, Any], sweep: list[dict[str, Any]]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    gate_pass = all(m["passed"] for m in metrics if m["passed"] is not None)
    report = {"meta": meta, "deployable": gate_pass and not meta.get("blockers"), "metrics": metrics,
              "counts": asdict(counts), "threshold_sweep": sweep}
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    with (out_dir / "predictions.jsonl").open("w", encoding="utf-8") as fh:
        for d in detail:
            p = preds.get(d["id"])
            fh.write(json.dumps({**d, "output": p.output if p else None, "attempts": p.attempts if p else 0,
                                 "infra_error": p.infra_error if p else "missing"}, ensure_ascii=False) + "\n")
    lines = [f"# ReceiptDesk model evaluation (NFR-01)", "",
             f"- model: `{meta.get('model')}`  backend: `{meta['backend']}`  at {meta['finished_at']}",
             f"- Test Set: {counts.n} readable + {counts.n_unreadable} unreadable receipts",
             f"- flags = web rules: confidence < {rc.CONFIDENCE_THRESHOLD} · |items − total| > "
             f"{rc.satang_to_str(rc.MISMATCH_LIMIT_SATANG)} baht", "",
             "| Metric | Value | Count | Rule | Result |", "|---|---|---|---|---|"]
    for m in metrics:
        unit = "" if m["id"] == "M5" else "%"
        res = "—" if m["passed"] is None else ("PASS" if m["passed"] else "FAIL")
        lines.append(f"| {m['id']} {m['name']} | {m['value']}{unit} | {m['num']}/{m['den']} | {m['rule']} | {res} |")
    verdict = "DEPLOYABLE (M1–M6 all pass)" if report["deployable"] else "NOT deployable"
    lines += ["", f"**Verdict: {verdict}**"]
    for b in meta.get("blockers", []):
        lines.append(f"- blocker: {b}")
    silent = [d["id"] for d in detail if d.get("silent_error")]
    lines += ["", f"Silent errors (wrong total, no flag): {', '.join(silent) or 'none'}",
              f"Flagged (valid answer): {counts.flagged_only} · failed reads → pile: "
              f"{counts.needs_review - counts.flagged_only}"]
    if sweep:
        lines += ["", "## Threshold sweep (informational, DESIGN D-02 — the gate above always uses 0.90)", "",
                  "| conf threshold | M2 silent | M3 recall | M4 flag rate | M5 |", "|---|---|---|---|---|"]
        for s in sweep:
            lines.append(f"| {s['threshold']} | {s['M2']}% | {s['M3']}% | {s['M4']}% | {s['M5']} |")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--test-set", help="readable Test Set JSONL (>= 200, may also contain unreadable rows)")
    p.add_argument("--unreadable-set", help="unreadable set JSONL (>= 20 rows, 'unreadable': true)")
    p.add_argument("--backend", choices=["vllm", "hf", "predictions"], default="vllm")
    p.add_argument("--vllm-url", default=os.environ.get("VLLM_URL", "http://127.0.0.1:8080"),
                   help="NGINX (8080) or one vLLM (8001/8002) on the GPU box")
    p.add_argument("--served-model", default=rc.SERVED_MODEL_NAME)
    p.add_argument("--api-key-env", default="VLLM_API_KEY", help="env var holding the vLLM key (never a literal)")
    p.add_argument("--model", help="hf backend: base model id/path")
    p.add_argument("--adapter", help="hf backend: LoRA dir from train_lora.py")
    p.add_argument("--predictions", help="predictions backend: JSONL with id/output/total_confidence")
    p.add_argument("--attempts", type=int, default=1, help="re-ask on invalid answer (production BR-07 = 3)")
    p.add_argument("--concurrency", type=int, default=8)
    p.add_argument("--timeout", type=float, default=60.0, help="seconds per request (DESIGN 6.3)")
    p.add_argument("--max-new-tokens", type=int, default=512)
    p.add_argument("--image-max-side", type=int, default=1600)
    p.add_argument("--sweep", default="0.80,0.85,0.90,0.95", help="extra confidence thresholds to report")
    p.add_argument("--out-dir", default=None, help="default <this dir>/eval-out/<timestamp>")
    p.add_argument("--allow-small-test-set", action="store_true", help="do not block on < 200 / < 20 rows")
    p.add_argument("--dry-run", action="store_true", help="CPU self-test + synthetic run (see docstring)")
    args = p.parse_args(argv)
    if args.attempts < 1 or args.attempts > 3:
        p.error("--attempts must be 1..3 (BR-07: never a 4th read)")
    if not args.dry_run:
        if not args.test_set:
            p.error("--test-set is required (or --dry-run)")
        if args.backend == "hf" and not args.model:
            p.error("--backend hf needs --model")
        if args.backend == "predictions" and not args.predictions:
            p.error("--backend predictions needs --predictions")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    out_dir = Path(args.out_dir or Path(__file__).resolve().parent / "eval-out" / time.strftime("%Y%m%d-%H%M%S"))
    blockers: list[str] = []
    expected: Counts | None = None
    server = None

    if args.dry_run:
        fails = self_test()
        for f in fails:
            LOG.error("self-test FAILED: %s", f)
        LOG.info("rule self-test: %d TEST-DATA/NFR-01 cases, %d failure(s)", 21 + 3, len(fails))
        if fails:
            return 1
        data = out_dir / "_dryrun"
        jsonl = data / "test.jsonl"
        if not jsonl.exists():
            rc.write_synthetic_dataset(data, n=MIN_READABLE, n_unreadable=MIN_UNREADABLE, seed=7, name="test")
        rows = rc.load_jsonl(jsonl)
        scripted, expected = scripted_outputs(rows)
        model_name = "scripted-fake-model"
        if args.backend == "predictions":  # default in dry-run: score scripted text directly
            preds = {rid: Prediction(rid, t, c) for rid, (t, c) in scripted.items()}
        elif args.backend == "vllm":
            server, url = start_fake_vllm(rows, scripted, args.image_max_side)
            client = VLLMClient(url, args.served_model, None, args.timeout, args.max_new_tokens,
                                args.image_max_side)
            preds = run_predictor(rows, client, args.attempts, args.concurrency)
            model_name = f"fake vLLM at {url}"
        else:  # hf: tiny random VLM, real generate() on CPU; only the pipeline is checked
            tiny = args.model or rc.build_tiny_vlm(out_dir / "_dryrun" / "tiny-model")
            rows = rows[:6] + rows[-2:]
            fn = HFPredictor(str(tiny), args.adapter, 320, min(args.max_new_tokens, 24), "fp32")
            preds = run_predictor(rows, fn, 1, 1)
            expected, model_name = None, "tiny-random-qwen2-vl"
    else:
        rows = rc.load_jsonl(args.test_set)
        if args.unreadable_set:
            extra = rc.load_jsonl(args.unreadable_set)
            for r in extra:
                r["unreadable"] = True
            rows += extra
        ids = [r["id"] for r in rows]
        if len(ids) != len(set(ids)):
            LOG.error("duplicate receipt ids in the Test Set")
            return 2
        n_read = sum(not r["unreadable"] for r in rows)
        n_unread = len(rows) - n_read
        if (n_read < MIN_READABLE or n_unread < MIN_UNREADABLE) and not args.allow_small_test_set:
            blockers.append(f"Test Set too small for NFR-01: {n_read} readable (need >= {MIN_READABLE}), "
                            f"{n_unread} unreadable (need >= {MIN_UNREADABLE})")
        if args.backend == "predictions":
            preds, model_name = load_predictions(args.predictions), args.predictions
        elif args.backend == "vllm":
            key = os.environ.get(args.api_key_env)
            client = VLLMClient(args.vllm_url, args.served_model, key, args.timeout, args.max_new_tokens,
                                args.image_max_side)
            preds, model_name = run_predictor(rows, client, args.attempts, args.concurrency), args.served_model
        else:
            fn = HFPredictor(args.model, args.adapter, args.image_max_side, args.max_new_tokens)
            preds = run_predictor(rows, fn, args.attempts, 1)
            model_name = f"{args.model} + {args.adapter or 'no adapter'}"

    infra = [p for p in preds.values() if p.infra_error]
    missing = [r["id"] for r in rows if r["id"] not in preds]
    if infra:
        blockers.append(f"{len(infra)} request(s) failed (e.g. {infra[0].infra_error}) — rerun, not a model score")
    if missing:
        blockers.append(f"{len(missing)} receipt(s) have no prediction (e.g. {missing[0]})")

    counts, detail = score(rows, preds)
    metrics = gate(counts)
    sweep = []
    for t in [x.strip() for x in args.sweep.split(",") if x.strip()]:
        c, _ = score(rows, preds, Decimal(t))
        g = {m["id"]: m["value"] for m in gate(c)}
        sweep.append({"threshold": t, "M2": g["M2"], "M3": g["M3"], "M4": g["M4"], "M5": g["M5"]})
    meta = {"backend": args.backend + (" (dry-run)" if args.dry_run else ""), "model": model_name,
            "prompt_sha256_16": hashlib.sha256((rc.SYSTEM_PROMPT + "\n" + rc.USER_PROMPT).encode()).hexdigest()[:16],
            "attempts": args.attempts, "blockers": blockers, "finished_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    write_report(out_dir, metrics, counts, detail, preds, meta, sweep)
    if server:
        server.shutdown()

    for m in metrics:
        res = "—" if m["passed"] is None else ("PASS" if m["passed"] else "FAIL")
        LOG.info("%-3s %-28s %8s  (%s/%s)  %-12s %s", m["id"], m["name"], m["value"], m["num"], m["den"],
                 m["rule"], res)
    for b in blockers:
        LOG.warning("blocker: %s", b)
    LOG.info("report: %s", out_dir / "report.md")

    if args.dry_run:
        if expected is not None and asdict(counts) != asdict(expected):
            LOG.error("dry-run: counts %s != expected %s", asdict(counts), asdict(expected))
            return 1
        if expected is None:
            LOG.info("DRY-RUN PASSED (hf): rules match TEST-DATA; real generate() + logprob confidence ran "
                     "end-to-end on CPU (random weights, so the model gate FAIL above is expected)")
        else:
            LOG.info("DRY-RUN PASSED (%s): rules match TEST-DATA, pipeline counts equal the scripted answers",
                     args.backend)
        return 0
    if blockers:
        return 2
    return 0 if all(m["passed"] for m in metrics if m["passed"] is not None) else 1


if __name__ == "__main__":
    sys.exit(main())
