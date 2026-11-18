"""ค่าส่งเมล็ดกาแฟ BaanKafe

คำนวณเป็นสตางค์ (1 บาท = 100 สตางค์) ด้วย Fraction เพื่อให้ไม่มีความคลาดเคลื่อนจากทศนิยมของ float
และปัดเศษผลลัพธ์สุดท้ายเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น)

กติกา:
- น้ำหนัก 1–30,000 กรัม
  - ไม่เกิน 1,000 กรัม  : 40 บาท
  - ไม่เกิน 5,000 กรัม  : 80 บาท
  - เกิน 5,000 กรัม     : 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน (คิดตามสัดส่วนของกรัม)
- ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
- ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อนหน้า)
"""

from fractions import Fraction
import math


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : น้ำหนักเป็นกรัม (1–30,000)
    distance_km : ระยะทางเป็นกิโลเมตร (ตั้งแต่ 0)
    express     : True = ส่งด่วน
    """
    w = Fraction(weight_g)
    d = Fraction(distance_km)

    if not (1 <= w <= 30000):
        raise ValueError("weight_g ต้องอยู่ในช่วง 1–30,000 กรัม")
    if d < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    # ค่าส่งฐาน (หน่วย: สตางค์)
    if w <= 1000:
        fee = Fraction(40 * 100)
    elif w <= 5000:
        fee = Fraction(80 * 100)
    else:
        # 15 บาท/กก. = 15 * 100 สตางค์ / 1000 กรัม = 1.5 สตางค์ต่อกรัม
        fee = Fraction(80 * 100) + (w - 5000) * Fraction(15 * 100, 1000)

    # ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if d > 100:
        fee *= Fraction(120, 100)

    # ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
    if express:
        fee *= Fraction(150, 100)

    # ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์
    return math.floor(fee + Fraction(1, 2))


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(shipping_fee(500, 10, False))     # 4000  (40 บาท)
    print(shipping_fee(1000, 10, False))    # 4000  (40 บาท)
    print(shipping_fee(1001, 10, False))    # 8000  (80 บาท)
    print(shipping_fee(6000, 10, False))    # 9500  (95 บาท)
    print(shipping_fee(6000, 150, True))    # 17100 (171 บาท)
