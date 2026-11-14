RATES = {"silver": 15, "gold": 25, "platinum": 40}  # ต่อ 1000
MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
CAP = 20000          # 200 บาท (สตางค์)


def _int(name, v, lo=None, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้อง >= {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} ต้อง <= {hi}")
    return v


def _bool(name, v):
    if not isinstance(v, bool):
        raise ValueError(f"{name} ต้องเป็น bool")
    return v


def cashback(amount, tier, birthday):
    _int("amount", amount, lo=0)
    if not isinstance(tier, str) or tier not in RATES:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    _bool("birthday", birthday)
    if amount < MIN_AMOUNT:
        return 0
    num = amount * RATES[tier] * (2 if birthday else 1)
    den = 1000
    result = (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น ครั้งเดียว
    return min(result, CAP)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = cashback(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
