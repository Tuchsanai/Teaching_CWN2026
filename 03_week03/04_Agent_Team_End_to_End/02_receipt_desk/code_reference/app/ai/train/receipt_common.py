"""Shared pieces for ReceiptDesk LoRA training (train_lora.py) and evaluation (evaluate.py).

Everything that must agree between training, evaluation and production lives here:

* the prompt the model is trained and served with (the GPU worker must send the same prompt)
* the 5-field output contract (merchant · date · items[name, price] · total) and its parser (M6)
* the flag rules, identical to the web rules module (BR-04 < 0.90, BR-05 > 1.00 baht, in satang)
* how ``total_confidence`` is derived from token log-probabilities (DESIGN D-02)
* dataset loading (JSONL + images), synthetic receipts and a tiny offline VLM for ``--dry-run``

Only the standard library and Pillow are imported at module level, so evaluate.py can score
pre-computed predictions on a machine without torch.
"""

from __future__ import annotations

import datetime as _dt
import json
import math
import os
import random
import re
import unicodedata
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

# --------------------------------------------------------------------------------------
# Business-rule constants: same numbers as the web (REQUIREMENTS BR-04, BR-05; NFR-01).
# --------------------------------------------------------------------------------------
CONFIDENCE_THRESHOLD = Decimal("0.90")  # BR-04: total_confidence < 0.90 -> flag "ไม่แน่ใจยอดรวม"
MISMATCH_LIMIT_SATANG = 100  # BR-05: |sum(items) - total| > 1.00 baht -> flag "ยอดไม่ตรงรายการ"

SERVED_MODEL_NAME = "receipt-vlm"  # name used by vLLM / gateway results (DESIGN 5.4)

SYSTEM_PROMPT = (
    "You are a receipt reader for a Thai accounting office. "
    "Read the receipt image and answer with ONE JSON object only, no other text."
)
USER_PROMPT = (
    "Read this receipt and return JSON with exactly these keys:\n"
    '{"merchant": string, "date": "YYYY-MM-DD", '
    '"items": [{"name": string, "price": "0.00"}], "total": "0.00"}\n'
    "- merchant: shop name as printed\n"
    "- date: receipt date in the Gregorian calendar (convert Buddhist Era years: subtract 543)\n"
    "- items: every line item with its printed price as a string with 2 decimals\n"
    "- total: the grand total printed on the receipt (do NOT compute it from the items)\n"
    'If the image is blurred, cut off or not a receipt, return {"unreadable": true} instead. '
    "Never guess a total you cannot read."
)
UNREADABLE_TARGET = {"unreadable": True}


# --------------------------------------------------------------------------------------
# Money: compared as integer satang (TEST-DATA section 0: 1.00 baht = 100 satang).
# --------------------------------------------------------------------------------------
_AMOUNT_RE = re.compile(r"^-?\d+(?:\.\d+)?$")


def parse_amount_satang(value: Any) -> int | None:
    """"100.00" / "1,000.5" / 99.5 -> satang (int), rounded half-up to 2 decimals. Invalid -> None."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            return None
        text = repr(value) if isinstance(value, float) else str(value)
    elif isinstance(value, str):
        text = value.strip().replace(",", "").replace("฿", "").replace("บาท", "").strip()
    else:
        return None
    if not _AMOUNT_RE.match(text):
        return None
    try:
        dec = Decimal(text).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        return None
    return int(dec * 100)


def satang_to_str(satang: int) -> str:
    sign = "-" if satang < 0 else ""
    satang = abs(satang)
    return f"{sign}{satang // 100}.{satang % 100:02d}"


def parse_confidence(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        dec = Decimal(str(value))
    except InvalidOperation:
        return None
    if not dec.is_finite():
        return None
    return dec


# --------------------------------------------------------------------------------------
# Flag rules (BR-04, BR-05) — must give the same answer as web/lib/rules.ts.
# --------------------------------------------------------------------------------------
def flag_low_confidence(total_confidence: Any, threshold: Decimal = CONFIDENCE_THRESHOLD) -> bool:
    """BR-04: flag when confidence < 0.90. Compared WITHOUT rounding (0.8999 -> flag, 0.90 -> no flag).

    A missing/invalid confidence cannot prove >= 0.90, so it is treated as "not sure" (flag).
    ``threshold`` exists only for the informational sweep in evaluate.py (DESIGN D-02).
    """
    conf = parse_confidence(total_confidence)
    return conf is None or conf < threshold


def flag_mismatch(item_prices_satang: Iterable[int], total_satang: int | None) -> bool:
    """BR-05: flag when |sum(item prices) - total| > 1.00 baht (100 satang). 1.00 exactly -> no flag."""
    if total_satang is None:
        return True
    return abs(sum(item_prices_satang) - total_satang) > MISMATCH_LIMIT_SATANG


# --------------------------------------------------------------------------------------
# Model output parsing (M6 "JSON validity": 5 fields present and well-typed).
# --------------------------------------------------------------------------------------
@dataclass
class ParsedOutput:
    valid: bool  # full 5-field structure (M6)
    unreadable: bool  # model explicitly answered {"unreadable": true}
    merchant: str | None = None
    date: str | None = None
    items: list[dict[str, Any]] = field(default_factory=list)  # [{"name": str, "price_satang": int}]
    total_satang: int | None = None
    error: str | None = None

    @property
    def has_total(self) -> bool:
        return self.total_satang is not None


_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def _extract_json_object(text: str) -> Any:
    text = _FENCE_RE.sub("", text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        return json.loads(text[start : end + 1])
    raise json.JSONDecodeError("no JSON object", text, 0)


def _valid_iso_date(value: Any) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        _dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def parse_model_output(raw: Any) -> ParsedOutput:
    """Parse the model's text (or an already-decoded dict) into the 5-field contract."""
    if isinstance(raw, dict):
        obj = raw
    else:
        try:
            obj = _extract_json_object(str(raw or ""))
        except (json.JSONDecodeError, ValueError):
            return ParsedOutput(valid=False, unreadable=False, error="not_json")
    if not isinstance(obj, dict):
        return ParsedOutput(valid=False, unreadable=False, error="not_object")
    if obj.get("unreadable") is True:
        return ParsedOutput(valid=False, unreadable=True, error="unreadable")

    out = ParsedOutput(valid=False, unreadable=False)
    out.total_satang = parse_amount_satang(obj.get("total"))
    problems = []
    merchant = obj.get("merchant")
    if isinstance(merchant, str) and merchant.strip():
        out.merchant = merchant.strip()
    else:
        problems.append("merchant")
    if _valid_iso_date(obj.get("date")):
        out.date = obj["date"]
    else:
        problems.append("date")
    items = obj.get("items")
    if isinstance(items, list):
        for it in items:
            if not isinstance(it, dict):
                problems.append("items")
                break
            name = it.get("name")
            price = parse_amount_satang(it.get("price"))
            if not (isinstance(name, str) and name.strip()):
                problems.append("item_name")
                break
            if price is None:
                problems.append("item_price")
                break
            out.items.append({"name": name.strip(), "price_satang": price})
    else:
        problems.append("items")
    if out.total_satang is None:
        problems.append("total")
    out.valid = not problems
    out.error = ",".join(problems) if problems else None
    return out


def flags_for(parsed: ParsedOutput, total_confidence: Any,
              threshold: Decimal = CONFIDENCE_THRESHOLD) -> tuple[bool, bool]:
    """(flag_low_confidence, flag_mismatch) exactly as the web would set them for a 'review' receipt."""
    low = flag_low_confidence(total_confidence, threshold)
    mismatch = flag_mismatch((i["price_satang"] for i in parsed.items), parsed.total_satang)
    return low, mismatch


# --------------------------------------------------------------------------------------
# total_confidence from token log-probabilities (DESIGN 3 / D-02).
# Definition: joint probability of the tokens that spell the "total" value =
#   exp(sum(logprob of every generated token overlapping the value's characters)).
# The GPU worker must compute it the same way so evaluation matches production.
# --------------------------------------------------------------------------------------
_TOTAL_VALUE_RE = re.compile(r'"total"\s*:\s*"?(-?[\d,]+(?:\.\d+)?)')


def total_value_span(text: str) -> tuple[int, int] | None:
    matches = list(_TOTAL_VALUE_RE.finditer(text))
    if not matches:
        return None
    m = matches[-1]
    return m.start(1), m.end(1)


def confidence_from_token_spans(text: str, spans: list[tuple[int, int, float]]) -> float | None:
    """spans = [(char_start, char_end, logprob)] of generated tokens, offsets into ``text``."""
    span = total_value_span(text)
    if span is None or not spans:
        return None
    s, e = span
    lps = [lp for (a, b, lp) in spans if a < e and b > s]
    if not lps:
        return None
    return float(math.exp(sum(lps)))


def spans_from_token_pieces(pieces: list[tuple[bytes | str, float]]) -> list[tuple[int, int, float]]:
    """Turn (token bytes-or-text, logprob) into char spans. Bytes handle split multi-byte Thai chars."""
    spans, buf, pos = [], b"", 0
    for piece, lp in pieces:
        if isinstance(piece, bytes):
            buf += piece
            end = len(buf.decode("utf-8", errors="ignore"))
        else:
            buf += piece.encode("utf-8")
            end = pos + len(piece)
        spans.append((pos, end, lp))
        pos = end
    return spans


# --------------------------------------------------------------------------------------
# Dataset records (JSONL). One line per receipt:
#   {"id": "r0001", "image": "images/r0001.jpg", "merchant": "...", "date": "2026-11-18",
#    "items": [{"name": "...", "price": "45.00"}], "total": "100.00"}
#   {"id": "u01", "image": "images/u01.jpg", "unreadable": true}
# Relative image paths are resolved against the JSONL file's directory.
# --------------------------------------------------------------------------------------
def load_jsonl(path: str | os.PathLike) -> list[dict[str, Any]]:
    path = Path(path)
    rows = []
    with path.open(encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            row = json.loads(line)
            if "image" not in row:
                raise ValueError(f"{path}:{n}: missing 'image'")
            img = Path(row["image"])
            row["image"] = str(img if img.is_absolute() else (path.parent / img))
            row.setdefault("id", f"{path.stem}-{n}")
            row["unreadable"] = bool(row.get("unreadable", False))
            if not row["unreadable"]:
                missing = [k for k in ("merchant", "date", "items", "total") if k not in row]
                if missing:
                    raise ValueError(f"{path}:{n}: readable receipt missing {missing}")
            rows.append(row)
    return rows


def target_text(row: dict[str, Any]) -> str:
    """Training target: the exact JSON string the model must produce (key order = DESIGN 5.4)."""
    if row.get("unreadable"):
        return json.dumps(UNREADABLE_TARGET, ensure_ascii=False)
    items = [
        {"name": str(it["name"]), "price": satang_to_str(parse_amount_satang(it["price"]))}
        for it in row["items"]
    ]
    obj = {
        "merchant": row["merchant"],
        "date": row["date"],
        "items": items,
        "total": satang_to_str(parse_amount_satang(row["total"])),
    }
    return json.dumps(obj, ensure_ascii=False, separators=(", ", ": "))


def build_messages(answer: str | None = None) -> list[dict[str, Any]]:
    msgs: list[dict[str, Any]] = [
        {"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPT}]},
        {"role": "user", "content": [{"type": "image"}, {"type": "text", "text": USER_PROMPT}]},
    ]
    if answer is not None:
        msgs.append({"role": "assistant", "content": [{"type": "text", "text": answer}]})
    return msgs


def load_image(path: str, max_side: int = 1600):
    """Open JPG/PNG (or the single page of a PDF, if pypdfium2 is installed) as RGB, longest side <= max_side."""
    from PIL import Image

    if path.lower().endswith(".pdf"):
        try:
            import pypdfium2 as pdfium  # optional
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("PDF receipts need `pip install pypdfium2`") from exc
        pdf = pdfium.PdfDocument(path)
        img = pdf[0].render(scale=200 / 72).to_pil()
    else:
        img = Image.open(path)
        img.load()
    img = img.convert("RGB")
    if max_side and max(img.size) > max_side:
        scale = max_side / max(img.size)
        img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))))
    return img


# --------------------------------------------------------------------------------------
# M7 helper: item-name F1 with "1–2 typos are fine" (Levenshtein <= 2).
# --------------------------------------------------------------------------------------
def _norm_name(s: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s)).strip().lower()


def _levenshtein(a: str, b: str, cap: int = 3) -> int:
    if abs(len(a) - len(b)) >= cap:
        return cap
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return min(prev[-1], cap)


def item_name_matches(pred: list[str], gold: list[str], max_edits: int = 2) -> int:
    gold_left = [_norm_name(g) for g in gold]
    hits = 0
    for p in (_norm_name(x) for x in pred):
        best = None
        for idx, g in enumerate(gold_left):
            if _levenshtein(p, g) <= max_edits:
                best = idx
                break
        if best is not None:
            gold_left.pop(best)
            hits += 1
    return hits


# --------------------------------------------------------------------------------------
# Synthetic receipts (for --dry-run only; ASCII text so the default PIL font can draw it).
# --------------------------------------------------------------------------------------
_SHOPS = ["Sample Shop", "Baan Rice", "Ice Mart", "Gas Depot", "Fresh Market", "ร้านตัวอย่าง"]
_GOODS = ["rice 5kg", "fish sauce", "ice bag", "gas tank", "eggs 30", "sugar 1kg", "oil 1L", "ข้าวสาร 5 กก."]


def synthetic_rows(n: int, n_unreadable: int, seed: int = 0) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        items = []
        for _ in range(rng.randint(1, 4)):
            items.append({"name": rng.choice(_GOODS), "price": satang_to_str(rng.randint(100, 50000))})
        total = sum(parse_amount_satang(it["price"]) for it in items)
        day = _dt.date(2026, 10, 1) + _dt.timedelta(days=rng.randint(0, 60))
        rows.append(
            {
                "id": f"syn-{i:04d}",
                "merchant": rng.choice(_SHOPS),
                "date": day.isoformat(),
                "items": items,
                "total": satang_to_str(total),
                "unreadable": False,
            }
        )
    for i in range(n_unreadable):
        rows.append({"id": f"syn-unreadable-{i:02d}", "unreadable": True})
    return rows


def render_receipt(row: dict[str, Any], seed: int = 0, size: tuple[int, int] = (224, 308)):
    from PIL import Image, ImageDraw, ImageFilter

    img = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(img)
    rng = random.Random(f"{seed}-{row['id']}")
    if row.get("unreadable"):
        lines = ["RECEIPT", f"{rng.randint(1, 999)}.{rng.randint(0, 99):02d}"] * 4
    else:
        lines = [row["merchant"], row["date"]]
        lines += [f"{it['name']:<12}{it['price']:>9}" for it in row["items"]]
        lines += ["-" * 21, f"TOTAL {row['total']:>15}"]
    y = 8
    for line in lines:  # default PIL font has no Thai glyphs: draw an ASCII stand-in (labels keep Thai)
        draw.text((8, y), line.encode("ascii", "replace").decode(), fill="black")
        y += 18
    if row.get("unreadable"):
        img = img.crop((0, 0, size[0], size[1] // 3)).resize(size)  # "cut off"
        img = img.filter(ImageFilter.GaussianBlur(radius=6))  # "blurred"
    return img


def write_synthetic_dataset(out_dir: str | os.PathLike, n: int, n_unreadable: int, seed: int = 0,
                            name: str = "data") -> Path:
    """Write images + <name>.jsonl into out_dir and return the JSONL path."""
    out_dir = Path(out_dir)
    (out_dir / "images").mkdir(parents=True, exist_ok=True)
    jsonl = out_dir / f"{name}.jsonl"
    with jsonl.open("w", encoding="utf-8") as fh:
        for row in synthetic_rows(n, n_unreadable, seed):
            rel = f"images/{row['id']}.png"
            render_receipt(row, seed).save(out_dir / rel)
            row = {**row, "image": rel}
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return jsonl


# --------------------------------------------------------------------------------------
# Tiny random Qwen2-VL built fully offline (no download) so --dry-run exercises the REAL
# code path (AutoProcessor + AutoModelForImageTextToText + chat template + LoRA) on CPU.
# --------------------------------------------------------------------------------------
_TINY_CHAT_TEMPLATE = (
    "{% for message in messages %}"
    "{% if loop.first and message['role'] != 'system' %}<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n{% endif %}"
    "<|im_start|>{{ message['role'] }}\n"
    "{% if message['content'] is string %}{{ message['content'] }}"
    "{% else %}{% for content in message['content'] %}"
    "{% if content['type'] == 'image' %}<|vision_start|><|image_pad|><|vision_end|>"
    "{% elif content['type'] == 'text' %}{{ content['text'] }}{% endif %}"
    "{% endfor %}{% endif %}<|im_end|>\n"
    "{% endfor %}"
    "{% if add_generation_prompt %}<|im_start|>assistant\n{% endif %}"
)
_TINY_SPECIALS = [
    "<|endoftext|>", "<|im_start|>", "<|im_end|>", "<|vision_start|>", "<|vision_end|>",
    "<|image_pad|>", "<|video_pad|>",
]


def build_tiny_vlm(out_dir: str | os.PathLike, seed: int = 0) -> Path:
    """Create a ~1M-parameter random Qwen2-VL (byte-level tokenizer) at out_dir; returns the path."""
    import torch
    from tokenizers import Tokenizer, decoders, models, pre_tokenizers
    from transformers import (
        PreTrainedTokenizerFast,
        Qwen2VLConfig,
        Qwen2VLForConditionalGeneration,
        Qwen2VLImageProcessor,
        Qwen2VLProcessor,
    )

    out_dir = Path(out_dir)
    if (out_dir / "config.json").exists() and (out_dir / "tokenizer.json").exists():
        return out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    byte_vocab = {ch: i for i, ch in enumerate(pre_tokenizers.ByteLevel.alphabet())}
    tok = Tokenizer(models.BPE(vocab=byte_vocab, merges=[]))
    tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False, use_regex=True)
    tok.decoder = decoders.ByteLevel()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tok, eos_token="<|im_end|>", pad_token="<|endoftext|>",
        additional_special_tokens=_TINY_SPECIALS[1:], chat_template=_TINY_CHAT_TEMPLATE,
    )
    tokenizer.add_special_tokens({"additional_special_tokens": _TINY_SPECIALS[1:]})
    ids = {t: tokenizer.convert_tokens_to_ids(t) for t in _TINY_SPECIALS}

    image_processor = Qwen2VLImageProcessor(min_pixels=56 * 56, max_pixels=224 * 308)
    extra = {}
    try:  # transformers >= 4.5x requires a video processor for Qwen2-VL even if unused
        from transformers import Qwen2VLVideoProcessor

        extra["video_processor"] = Qwen2VLVideoProcessor()
    except ImportError:  # pragma: no cover - older transformers
        pass
    processor = Qwen2VLProcessor(image_processor=image_processor, tokenizer=tokenizer,
                                 chat_template=_TINY_CHAT_TEMPLATE, **extra)

    torch.manual_seed(seed)
    config = Qwen2VLConfig(
        text_config=dict(
            vocab_size=len(tokenizer), hidden_size=64, intermediate_size=128, num_hidden_layers=2,
            num_attention_heads=4, num_key_value_heads=2, max_position_embeddings=4096,
            rope_parameters={"rope_type": "default", "rope_theta": 10000.0, "mrope_section": [2, 3, 3]},
            bos_token_id=ids["<|endoftext|>"], eos_token_id=ids["<|im_end|>"], pad_token_id=ids["<|endoftext|>"],
        ),
        vision_config=dict(depth=1, embed_dim=32, hidden_size=64, num_heads=2, mlp_ratio=2,
                           patch_size=14, spatial_merge_size=2, temporal_patch_size=2),
        image_token_id=ids["<|image_pad|>"], video_token_id=ids["<|video_pad|>"],
        vision_start_token_id=ids["<|vision_start|>"], vision_end_token_id=ids["<|vision_end|>"],
    )
    model = Qwen2VLForConditionalGeneration(config)
    model.generation_config.eos_token_id = ids["<|im_end|>"]
    model.generation_config.pad_token_id = ids["<|endoftext|>"]
    model.save_pretrained(out_dir)
    processor.save_pretrained(out_dir)
    return out_dir
