from fractions import Fraction
import math

EXPRESS_MAX_G = 20000  # สมมติฐาน: ส่งด่วนรับได้ไม่เกิน 20,000 กรัม (เกิน -> ValueError)


def shipping_fee(weight_g, distance_km, express):
    # --- ตรวจอินพุตก่อนทุกอย่าง ---
    if type(weight_g) is not int or not (1 <= weight_g <= 30000):
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม 1-30000")
    if type(distance_km) not in (int, float):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if type(distance_km) is float and not math.isfinite(distance_km):
        raise ValueError("distance_km ไม่ถูกต้อง")
    if distance_km < 0:
        raise ValueError("distance_km ต้อง >= 0")
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น True/False")
    if express and weight_g > EXPRESS_MAX_G:
        raise ValueError("ส่งด่วนรับน้ำหนักไม่เกิน 20,000 กรัม")

    # สมมติฐาน: ระยะ 0 กม. = รับเองที่ร้าน -> ค่าส่ง 0
    if distance_km == 0:
        return 0

    # --- คำนวณเป็นสตางค์ ด้วย Fraction ---
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction(1500 * (weight_g - 5000), 1000)

    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)

    # ปัดครึ่งขึ้นครั้งเดียวตอนจบ (เงินที่ลูกค้าจ่าย)
    return int((fee * 2 + 1) // 2)
