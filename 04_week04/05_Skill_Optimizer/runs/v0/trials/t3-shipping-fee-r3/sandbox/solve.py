import json
import math
import sys


def _is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (คำนวณด้วยจำนวนเต็ม ปัดครึ่งขึ้นครั้งเดียวตอนท้าย)"""
    if not _is_num(weight_g) or not math.isfinite(weight_g) or weight_g != int(weight_g):
        raise ValueError("weight_g ต้องเป็นจำนวนเต็มกรัม")
    weight_g = int(weight_g)
    if not 1 <= weight_g <= 30000:
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1 ถึง 30000")
    if not _is_num(distance_km) or not math.isfinite(distance_km) or distance_km < 0:
        raise ValueError("distance_km ต้องเป็นตัวเลขตั้งแต่ 0")
    if not isinstance(express, bool):
        raise ValueError("express ต้องเป็น true/false")

    # เก็บเป็นเศษส่วน num/den (หน่วยสตางค์)
    if weight_g <= 1000:
        num, den = 4000, 1
    elif weight_g <= 5000:
        num, den = 8000, 1
    else:
        # 15 บาท/กก. = 1.5 สตางค์/กรัม
        num, den = 8000 * 2 + (weight_g - 5000) * 3, 2
    if distance_km > 100:
        num, den = num * 6, den * 5
    if express:
        num, den = num * 3, den * 2
    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น


def main(argv):
    try:
        raw = argv[1] if len(argv) > 1 else sys.stdin.read()
        d = json.loads(raw)
        out = {"fee_satang": shipping_fee(d["weight_g"], d["distance_km"], d["express"])}
        code = 0
    except (ValueError, KeyError, TypeError) as e:
        out = {"error": f"input ไม่ถูกต้อง: {e}"}
        code = 1
    print(json.dumps(out, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
