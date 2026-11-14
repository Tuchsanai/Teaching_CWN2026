import math
from fractions import Fraction


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


def _num(name, v, lo):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    if isinstance(v, float) and not math.isfinite(v):
        raise ValueError(f"{name} ต้องเป็นจำนวนจำกัด")
    if v < lo:
        raise ValueError(f"{name} ต้อง >= {lo}")
    return v


def shipping_fee(weight_g, distance_km, express):
    _int("weight_g", weight_g, 1, 30000)
    _num("distance_km", distance_km, 0)
    _bool("express", express)

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์ต่อ 1000 กรัม
        fee = 8000 + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    # ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = shipping_fee(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
