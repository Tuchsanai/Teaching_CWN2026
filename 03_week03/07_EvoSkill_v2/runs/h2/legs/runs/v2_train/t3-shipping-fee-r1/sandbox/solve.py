import math
from fractions import Fraction


def to_frac(x):
    """รับได้ทั้ง int, float, Decimal โดยไม่เกิดคลาดเคลื่อนจาก float"""
    return Fraction(str(x))


def round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม ใช้ครั้งเดียวตอนคืนค่า (ยอดไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def _to_number(name, value):
    if isinstance(value, bool):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    try:
        return to_frac(value)
    except (ValueError, TypeError, ArithmeticError):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")


def shipping_fee(weight_g, distance_km, express):
    """คิดค่าส่งเมล็ดกาแฟ คืนค่าเป็นจำนวนเต็มสตางค์

    1. ค่าส่งตามน้ำหนัก:
       - ไม่เกิน 1,000 กรัม           = 40 บาท
       - ไม่เกิน 5,000 กรัม (>1,000)  = 80 บาท
       - เกิน 5,000 กรัม              = 80 บาท + (กรัมที่เกิน 5,000 / 1,000) * 15 บาท
    2. ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (คูณ 1.2)
    3. ส่งด่วน คิดเพิ่ม 50% ต่อจากข้อ 2 (คูณ 1.5)
    4. ปัดครึ่งขึ้นครั้งเดียวที่ผลสุดท้ายเป็นสตางค์
    """
    weight = _to_number("weight_g", weight_g)
    distance = _to_number("distance_km", distance_km)

    if not (1 <= weight <= 30000):
        raise ValueError("weight_g ต้องอยู่ในช่วง 1–30,000 กรัม")
    if distance < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    if weight <= 1000:
        fee = Fraction(40)
    elif weight <= 5000:
        fee = Fraction(80)
    else:
        fee = Fraction(80) + (weight - 5000) / 1000 * 15

    if distance > 100:
        fee *= Fraction(12, 10)

    if express:
        fee *= Fraction(3, 2)

    return round_half_up(fee * 100)
