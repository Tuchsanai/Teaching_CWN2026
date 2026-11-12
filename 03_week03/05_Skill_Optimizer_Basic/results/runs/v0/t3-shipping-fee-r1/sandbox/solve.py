import json
import math
import sys
from fractions import Fraction


def _round_half_up(x: Fraction) -> int:
    return (x * 2 + 1) // 2


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (คำนวณด้วย Fraction ไม่ใช้ float, ปัดครั้งเดียวตอนท้าย)"""
    if isinstance(weight_g, bool) or not isinstance(weight_g, int):
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม (กรัม)")
    if not 1 <= weight_g <= 30000:
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1 ถึง 30000")
    if isinstance(distance_km, bool) or not isinstance(distance_km, (int, float)):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if isinstance(distance_km, float) and not math.isfinite(distance_km):
        raise ValueError("distance_km ต้องเป็นตัวเลขจำกัด")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")
    if not isinstance(express, bool):
        raise ValueError("express ต้องเป็น true/false")

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 กรัม
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return _round_half_up(fee)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        raw = argv[0] if argv else sys.stdin.read()
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("input ต้องเป็น JSON object")
        missing = [k for k in ("weight_g", "distance_km", "express") if k not in data]
        if missing:
            raise ValueError("ขาดฟิลด์: " + ", ".join(missing))
        out = {"satang": shipping_fee(data["weight_g"], data["distance_km"], data["express"])}
        print(json.dumps(out))
        return 0
    except (ValueError, TypeError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
