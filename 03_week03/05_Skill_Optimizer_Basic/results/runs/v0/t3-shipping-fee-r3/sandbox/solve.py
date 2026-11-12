import json
import math
import sys
from fractions import Fraction


def _num(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float, Fraction)):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{name} ต้องเป็นจำนวนจำกัด")
        return Fraction(repr(value))
    return Fraction(value)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (คำนวณด้วยเศษส่วนแท้ ปัดครั้งเดียวตอนท้าย half-up)"""
    w = _num(weight_g, "weight_g")
    d = _num(distance_km, "distance_km")
    if not isinstance(express, bool):
        raise ValueError("express ต้องเป็น True/False")
    if not (1 <= w <= 30000):
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1 ถึง 30000")
    if d < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + (w - 5000) * Fraction(1500, 1000)  # 15 บาท/กก. = 1.5 สตางค์/กรัม
    if d > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return math.floor(fee + Fraction(1, 2))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        raw = argv[0] if argv else sys.stdin.read()
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("input ต้องเป็น JSON object")
        missing = [k for k in ("weight_g", "distance_km") if k not in data]
        if missing:
            raise ValueError("ขาดฟิลด์: " + ", ".join(missing))
        fee = shipping_fee(data["weight_g"], data["distance_km"], data.get("express", False))
        print(json.dumps({"fee_satang": fee}))
        return 0
    except (ValueError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
