"""BaanKafe: คิดค่าส่งเมล็ดกาแฟ คืนค่าเป็นจำนวนเต็มสตางค์

ลำดับการคิด (ทำตามโจทย์ทุกขั้น):
  1. ค่าส่งฐานตามน้ำหนัก (บาท)
       - ไม่เกิน 1,000 กรัม          -> 40 บาท
       - 1,001 ถึง 5,000 กรัม        -> 80 บาท
       - เกิน 5,000 กรัม            -> 80 บาท + 15 บาท ต่อกิโลกรัมของส่วนที่เกิน 5,000 กรัม
                                       (คิดตามสัดส่วนของกรัม ไม่ปัดเป็นกิโล)
  2. ระยะทางเกิน 100 กม.  -> คูณ 1.20 (เพิ่ม 20%)
  3. ส่งด่วน (express=True) -> คูณ 1.50 (เพิ่ม 50%) ต่อจากข้อ 2
  4. แปลงเป็นสตางค์ (x 100) แล้วปัดครึ่งขึ้นที่ขั้นสุดท้ายครั้งเดียว

คำนวณด้วย Fraction ทั้งหมดเพื่อไม่ให้ float คลาด
โหมดการปัด: ปัดครึ่งขึ้น (half-up) ที่ขั้นสุดท้าย
"""

from fractions import Fraction
import math


def _to_fraction(x):
    """แปลงค่าตัวเลขเป็น Fraction โดยใช้ค่าทศนิยมตามที่เขียน (เช่น 100.5 -> 201/2)"""
    if isinstance(x, float):
        return Fraction(repr(x))
    return Fraction(x)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (int)

    weight_g    : น้ำหนักเป็นกรัม 1–30,000
    distance_km : ระยะทางเป็นกิโลเมตร (ตั้งแต่ 0)
    express     : True = ส่งด่วน
    """
    w = _to_fraction(weight_g)
    d = _to_fraction(distance_km)

    if not (1 <= w <= 30000):
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1 ถึง 30,000 กรัม")
    if d < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    # 1) ค่าส่งฐานตามน้ำหนัก (บาท)
    if w <= 1000:
        base_baht = Fraction(40)
    elif w <= 5000:
        base_baht = Fraction(80)
    else:
        base_baht = Fraction(80) + Fraction(15) * (w - 5000) / 1000

    # 2) แปลงเป็นสตางค์
    fee = base_baht * 100

    # 3) ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if d > 100:
        fee *= Fraction(120, 100)

    # 4) ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
    if express:
        fee *= Fraction(150, 100)

    # 5) ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (ค่าไม่ติดลบ)
    return int(math.floor(fee + Fraction(1, 2)))


if __name__ == "__main__":
    print(shipping_fee(1000, 50, False))   # 4000 สตางค์ (40 บาท)
    print(shipping_fee(1001, 50, False))   # 8000 สตางค์ (80 บาท)
    print(shipping_fee(5001, 50, False))   # 8002 สตางค์ (80.015 บาท ปัดครึ่งขึ้น)
    print(shipping_fee(10000, 120, True))  # ตัวอย่างรวมทุกเงื่อนไข
