import math
from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    if type(weight_g) is not int:
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม")
    if weight_g < 1:
        raise ValueError("weight_g ต้องไม่น้อยกว่า 1")
    if weight_g > 30000:
        raise ValueError("weight_g ต้องไม่เกิน 30000")
    if type(distance_km) not in (int, float):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if isinstance(distance_km, float) and not math.isfinite(distance_km):
        raise ValueError("distance_km ต้องเป็นค่าจำกัด")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่น้อยกว่า 0")
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น bool")

    if weight_g <= 1000:
        satang = Fraction(4000)
    elif weight_g <= 5000:
        satang = Fraction(8000)
    else:
        # 15 บาท/กก. = 1.5 สตางค์/กรัม
        satang = Fraction(8000) + Fraction((weight_g - 5000) * 3, 2)
    if distance_km > 100:
        satang *= Fraction(6, 5)
    if express:
        satang *= Fraction(3, 2)
    # ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย
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
