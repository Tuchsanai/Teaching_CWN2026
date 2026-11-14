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


def refund(paid, used_percent, restock):
    _int("paid", paid, 0)
    _int("used_percent", used_percent, 0, 100)
    _bool("restock", restock)
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7  # เหลือ 87.5% = 7/8
        den *= 8
    return (2 * num + den) // (2 * den)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = refund(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
