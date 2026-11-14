def _int(name, v, lo=None, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้อง >= {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} ต้อง <= {hi}")
    return v


def late_fee(amount, days_late):
    _int("amount", amount, lo=0)
    _int("days_late", days_late, lo=0, hi=365)
    if days_late <= 3:
        return 0
    bp = min(75 * days_late, 1500)  # หน่วย 1/10000 ของยอด (0.75%/วัน, เพดาน 15%)
    num, den = amount * bp, 10000
    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น ครั้งเดียว


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = late_fee(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
