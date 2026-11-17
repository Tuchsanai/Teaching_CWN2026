"""ส่วนที่ใช้ร่วมกัน: พรอมต์, การแปลงตัวเลข, การแปลงเฉลย CORD-v2 เป็น schema เป้าหมาย, การให้คะแนน"""
import json
import re
from collections import Counter

MODEL_ID = "Qwen/Qwen3-VL-2B-Instruct"
MAX_SIDE = 1280  # ด้านยาวสุดของภาพ (pixel) ใช้ค่าเดียวกันทั้งตอนเทรน ตอนวัดผล และในเว็บ

# พรอมต์เดียวกันทุกที่: เทรน, วัด Base, วัด Fine-tuned, เว็บ (web/lib/prompt.ts ต้องตรงกับข้อความนี้)
PROMPT = (
    "Read this receipt and return ONLY one JSON object with exactly this schema:\n"
    '{"items":[{"name":string,"qty":integer,"price":integer}],'
    '"subtotal":integer|null,"tax":integer|null,"total":integer|null}\n'
    "Rules: items = every purchased line in the order printed; price = the amount printed on that line; "
    "qty = 1 when no quantity is printed; numbers are integers without thousands separators or currency "
    '(for example "25,000" -> 25000); use null for a value that is not printed. '
    "No explanation and no markdown."
)


def to_int(v):
    """'Rp. 25,000' -> 25000 · '60.000' -> 60000 · '2.00' -> 2 · ไม่มีตัวเลข -> None"""
    if v is None:
        return None
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return int(round(v))
    if isinstance(v, list):
        v = v[0] if v else ""
    s = str(v).strip()
    s = re.sub(r"[.,]\d{2}$", "", s)  # ตัดทศนิยม 2 ตำแหน่งท้ายสุด (.00)
    digits = re.sub(r"\D", "", s)
    return int(digits) if digits else None


def _text(v):
    if isinstance(v, list):
        v = " ".join(str(x) for x in v)
    return re.sub(r"\s+", " ", str(v or "")).strip()


def gt_to_target(gt_parse):
    """แปลง gt_parse ของ CORD-v2 เป็น schema เป้าหมาย"""
    menu = gt_parse.get("menu") or []
    if isinstance(menu, dict):
        menu = [menu]
    items = []

    def add(it):
        if not isinstance(it, dict) or not _text(it.get("nm")):
            return
        qty = to_int(it.get("cnt"))
        items.append({"name": _text(it["nm"]), "qty": qty if qty else 1, "price": to_int(it.get("price"))})

    for it in menu:
        add(it)
        subs = it.get("sub") if isinstance(it, dict) else None
        for sub in ([subs] if isinstance(subs, dict) else subs or []):
            add(sub)  # รายการย่อย (เช่น topping) นับเป็นอีก 1 บรรทัด

    sub_total = gt_parse.get("sub_total") or {}
    total = gt_parse.get("total") or {}
    if isinstance(sub_total, list):
        sub_total = sub_total[0] if sub_total else {}
    if isinstance(total, list):
        total = total[0] if total else {}
    return {
        "items": items,
        "subtotal": to_int(sub_total.get("subtotal_price")),
        "tax": to_int(sub_total.get("tax_price")),
        "total": to_int(total.get("total_price")),
    }


def target_text(target):
    return json.dumps(target, ensure_ascii=False, separators=(",", ":"))


def parse_output(text):
    """ดึง JSON จากคำตอบของโมเดล · คืน dict หรือ None ถ้า parse ไม่ได้หรือไม่มี items เป็น list"""
    if not text:
        return None
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    a, b = t.find("{"), t.rfind("}")
    if a < 0 or b <= a:
        return None
    try:
        obj = json.loads(t[a : b + 1])
    except Exception:
        return None
    if not isinstance(obj, dict) or not isinstance(obj.get("items"), list):
        return None
    return obj


def norm_name(s):
    return re.sub(r"[^a-z0-9]", "", _text(s).lower())


def item_pairs(obj):
    """รายการสินค้าเป็น multiset ของ (ชื่อ, ราคา)"""
    out = Counter()
    for it in (obj or {}).get("items") or []:
        if isinstance(it, dict):
            out[(norm_name(it.get("name")), to_int(it.get("price")))] += 1
    return out


def score_one(pred, target):
    """คะแนนของใบเสร็จ 1 ใบ · pred = dict ที่ parse แล้ว หรือ None"""
    p, g = item_pairs(pred), item_pairs(target)
    tp = sum((p & g).values())
    return {
        "json_ok": pred is not None,
        "total_ok": pred is not None and target["total"] is not None and to_int(pred.get("total")) == target["total"],
        "has_total": target["total"] is not None,
        "tp": tp,
        "n_pred": sum(p.values()),
        "n_gt": sum(g.values()),
    }


def summarize(rows):
    """รวมคะแนนทั้งชุด · F1 แบบ micro (นับรวมทุกใบ)"""
    n = len(rows)
    tp = sum(r["tp"] for r in rows)
    n_pred = sum(r["n_pred"] for r in rows)
    n_gt = sum(r["n_gt"] for r in rows)
    prec = tp / n_pred if n_pred else 0.0
    rec = tp / n_gt if n_gt else 0.0
    return {
        "n": n,
        "json_ok_pct": round(100 * sum(r["json_ok"] for r in rows) / n, 1),
        "total_exact_pct": round(100 * sum(r["total_ok"] for r in rows) / max(1, sum(r["has_total"] for r in rows)), 1),
        "item_precision_pct": round(100 * prec, 1),
        "item_recall_pct": round(100 * rec, 1),
        "item_f1_pct": round(100 * (2 * prec * rec / (prec + rec) if prec + rec else 0.0), 1),
        "sec_per_receipt": round(sum(r["sec"] for r in rows) / n, 2),
    }
