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


def shipping_fee(weight_g, distance_km, express):
    _int("weight_g", weight_g, 1, 30000)
    if isinstance(distance_km, bool) or not isinstance(distance_km, (int, float)):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if isinstance(distance_km, float) and not math.isfinite(distance_km):
        raise ValueError("distance_km ต้องเป็นจำนวนจำกัด")
    if distance_km < 0:
        raise ValueError("distance_km ต้อง >= 0")
    _bool("express", express)

    # หน่วยสตางค์ (Fraction)
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 กรัม
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    # ปัดครึ่งขึ้นครั้งเดียว
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
