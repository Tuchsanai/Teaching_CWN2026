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


def cafe_bill(items, member):
    if not isinstance(items, list):
        raise ValueError("items ต้องเป็น list")
    _bool("member", member)
    total = 0
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            raise ValueError(f"items[{i}] ต้องเป็น dict")
        for k in ("price", "qty"):
            if k not in it:
                raise ValueError(f"items[{i}] ขาด key {k}")
        price = _int(f"items[{i}].price", it["price"], 0)
        qty = _int(f"items[{i}].qty", it["qty"], 1)
        total += price * qty

    num, den = total, 1
    if total >= 50000:  # 500 บาท
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (2 * num + den) // (2 * den)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = cafe_bill(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
