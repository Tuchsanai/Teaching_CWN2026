"""ค่าส่งเมล็ดกาแฟ BaanKafe"""

import math
from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : น้ำหนัก 1–30,000 กรัม
    distance_km : ระยะทาง (ตั้งแต่ 0 กม.)
    express     : True = ส่งด่วน
    """
    if not (1 <= weight_g <= 30000):
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1 ถึง 30,000 กรัม")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ต่ำกว่า 0")

    # ใช้ Fraction เพื่อให้คำนวณแบบแม่นยำ ไม่คลาดเคลื่อนจากทศนิยมของ float
    w = Fraction(weight_g)

    # ค่าส่งฐาน (บาท)
    if w <= 1000:
        fee = Fraction(40)
    elif w <= 5000:
        fee = Fraction(80)
    else:
        # เกิน 5,000 กรัม: 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน (คิดตามสัดส่วนกรัม)
        fee = Fraction(80) + (w - 5000) * Fraction(15, 1000)

    # ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if Fraction(distance_km) > 100:
        fee *= Fraction(6, 5)

    # ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
    if express:
        fee *= Fraction(3, 2)

    # แปลงเป็นสตางค์ แล้วปัดเศษแบบ half-up ให้เป็นจำนวนเต็ม
    satang = fee * 100
    return math.floor(satang + Fraction(1, 2))


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(shipping_fee(500, 50, False))     # 4000  (40 บาท)
    print(shipping_fee(2000, 150, True))    # 14400 (80 × 1.2 × 1.5 = 144 บาท)
    print(shipping_fee(8000, 0, True))      # 18750 (125 × 1.5 = 187.50 บาท)
    print(shipping_fee(6001, 0, False))     # 9502  (95.015 บาท → 9501.5 สตางค์ ปัดขึ้น)
