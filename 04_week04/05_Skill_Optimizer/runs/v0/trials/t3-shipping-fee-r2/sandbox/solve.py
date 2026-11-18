import json
import math
import sys
from fractions import Fraction


def _num(v, name):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    if isinstance(v, float) and not math.isfinite(v):
        raise ValueError(f"{name} ต้องเป็นจำนวนจำกัด")
    return Fraction(str(v)) if isinstance(v, float) else Fraction(v)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (คำนวณด้วยเศษส่วนแม่นยำ ปัดครึ่งขึ้นครั้งเดียวตอนท้าย)"""
    w = _num(weight_g, "weight_g")
    d = _num(distance_km, "distance_km")
    if not 1 <= w <= 30000:
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1–30000")
    if d < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")
    if not isinstance(express, bool):
        raise ValueError("express ต้องเป็น true/false")

    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + (w - 5000) * Fraction(3, 2)  # 15 บาท/กก. = 1.5 สตางค์/กรัม
    if d > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return math.floor(fee + Fraction(1, 2))


def main():
    try:
        data = json.loads(sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input ต้องเป็น JSON object")
        missing = {"weight_g", "distance_km", "express"} - data.keys()
        if missing:
            raise ValueError("ขาดฟิลด์: " + ", ".join(sorted(missing)))
        fee = shipping_fee(data["weight_g"], data["distance_km"], data["express"])
        print(json.dumps({"fee_satang": fee}))
    except ValueError as e:  # รวม JSONDecodeError
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
