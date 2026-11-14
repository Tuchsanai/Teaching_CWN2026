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


def bulk_price(unit_price, qty, coupon):
    _int("unit_price", unit_price, 0)
    _int("qty", qty, 1, 1000)
    _bool("coupon", coupon)

    # ตัวเศษ/ตัวส่วนสะสม ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
    num = unit_price * qty
    den = 1
    if qty >= 50:
        num *= 925   # ลด 7.5%
        den *= 1000
    elif qty >= 10:
        num *= 965   # ลด 3.5%
        den *= 1000
    if coupon:
        num *= 975   # ลดอีก 2.5%
        den *= 1000
    num *= 107       # VAT 7%
    den *= 100
    return (2 * num + den) // (2 * den)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = bulk_price(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
