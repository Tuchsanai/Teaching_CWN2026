"""BaanKafe shipping fee (สตางค์)
สมมติฐาน:
- distance_km รับ int หรือ float (ไม่รวม bool, ไม่รวม nan/inf) ตั้งแต่ 0; ระยะ 0 ใช้สูตรปกติ
- weight_g ต้องเป็น int 1–30000
- ค่าส่งเป็นเงินที่ลูกค้าจ่าย -> คำนวณด้วย Fraction ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
"""
import math
from fractions import Fraction


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    if type(weight_g) is not int or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม 1-30000")
    if type(distance_km) not in (int, float):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if type(distance_km) is float and not math.isfinite(distance_km):
        raise ValueError("distance_km ไม่ถูกต้อง")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น True หรือ False")

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1.5 สตางค์/กรัม
        fee = Fraction(8000) + Fraction(weight_g - 5000) * Fraction(3, 2)
    if Fraction(distance_km) > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return half_up(fee)
