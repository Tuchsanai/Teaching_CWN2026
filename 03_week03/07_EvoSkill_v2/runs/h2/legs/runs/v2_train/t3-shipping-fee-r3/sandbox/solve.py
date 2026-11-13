import math
from fractions import Fraction


def to_frac(x):
    """รับได้ทั้ง int, float, Decimal โดยไม่เกิดคลาดเคลื่อนจาก float"""
    return Fraction(str(x))


def round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม ใช้ครั้งเดียวตอนคืนค่า (ยอดไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def _check_number(name, x):
    if isinstance(x, bool):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    try:
        return to_frac(x)
    except (ValueError, TypeError, ArithmeticError):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")


def shipping_fee(weight_g, distance_km, express):
    """คำนวณค่าส่งเมล็ดกาแฟ คืนค่าเป็นจำนวนเต็มสตางค์

    ลำดับการคิด:
      1. ค่าส่งตามน้ำหนัก (บาท)
         - ไม่เกิน 1,000 กรัม          -> 40 บาท
         - เกิน 1,000 ถึง 5,000 กรัม   -> 80 บาท
         - เกิน 5,000 กรัม             -> 80 บาท + (กรัมที่เกิน 5,000 / 1,000) * 15 บาท
           (คิดตามสัดส่วน ไม่ปัดเป็นกิโลกรัมเต็ม)
      2. ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (คูณ 1.2)
      3. ส่งด่วน คิดเพิ่ม 50% ต่อจากข้อ 2 (คูณ 1.5)
      4. ปัดครึ่งขึ้นครั้งเดียวที่ผลสุดท้ายเป็นสตางค์
    """
    w = _check_number("weight_g", weight_g)
    d = _check_number("distance_km", distance_km)

    if not (Fraction(1) <= w <= Fraction(30000)):
        raise ValueError("weight_g ต้องอยู่ในช่วง 1–30,000 กรัม")
    if d < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")
    if not isinstance(express, bool):
        raise ValueError("express ต้องเป็น True หรือ False")

    # 1) ค่าส่งตามน้ำหนัก (บาท)
    if w <= 1000:
        fee = Fraction(40)
    elif w <= 5000:
        fee = Fraction(80)
    else:
        fee = Fraction(80) + (w - 5000) / 1000 * Fraction(15)

    # 2) ระยะทางเกิน 100 กม. เพิ่ม 20%
    if d > 100:
        fee *= Fraction(120, 100)

    # 3) ส่งด่วนเพิ่ม 50% (คิดต่อจากข้อก่อน)
    if express:
        fee *= Fraction(150, 100)

    # 4) แปลงเป็นสตางค์และปัดครึ่งขึ้นครั้งเดียว
    return round_half_up(fee * 100)


if __name__ == "__main__":
    print(shipping_fee(2500, 50, False))  # 8000
