from fractions import Fraction
import math


def _need_int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} ต้องไม่เกิน {hi}")


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้นครั้งเดียวตอนท้าย)"""
    _need_int("weight_g", weight_g, 1, 30000)
    if type(distance_km) not in (int, float):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if isinstance(distance_km, float) and not math.isfinite(distance_km):
        raise ValueError("distance_km ต้องเป็นจำนวนจำกัด")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่น้อยกว่า 0")
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น bool")
    if express and weight_g > 20000:
        raise ValueError("ส่งด่วนรับน้ำหนักไม่เกิน 20000 กรัม")

    # ระยะทาง 0 = ลูกค้ารับเองที่ร้าน ไม่คิดค่าส่ง
    if distance_km == 0:
        return 0

    if weight_g <= 1000:
        fee = Fraction(40)
    elif weight_g <= 5000:
        fee = Fraction(80)
    else:
        fee = 80 + Fraction(weight_g - 5000, 1000) * 15
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    satang = fee * 100
    return math.floor(satang + Fraction(1, 2))


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = shipping_fee(**data)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)
