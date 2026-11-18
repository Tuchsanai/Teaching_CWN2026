from fractions import Fraction
import math


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้นครั้งเดียวตอนท้าย)"""
    if type(weight_g) is not int:
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม")
    if weight_g < 1 or weight_g > 30000:
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1 ถึง 30000")
    if type(distance_km) not in (int, float):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if type(distance_km) is float and not math.isfinite(distance_km):
        raise ValueError("distance_km ต้องเป็นตัวเลขจำกัด")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่น้อยกว่า 0")
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น bool")
    if express and weight_g > 20000:
        raise ValueError("ส่งด่วนรับน้ำหนักไม่เกิน 20000 กรัม")

    # ระยะทาง 0 = รับเองที่ร้าน ไม่คิดค่าส่ง
    if distance_km == 0:
        return 0

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 กรัม ตามสัดส่วน
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return math.floor(fee + Fraction(1, 2))


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
