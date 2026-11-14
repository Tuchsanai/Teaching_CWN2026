"""คิดค่าส่งเมล็ดกาแฟ BaanKafe

ลำดับการคิด (ตามโจทย์):
1. ค่าส่งฐานตามน้ำหนัก (คำนวณเป็นบาทแบบ Fraction ไม่ปัดระหว่างทาง)
   - 1–1,000 กรัม            = 40 บาท
   - 1,001–5,000 กรัม        = 80 บาท
   - เกิน 5,000 กรัม         = 80 บาท + (กรัมที่เกิน 5,000 / 1,000) × 15 บาท (สัดส่วนเส้นตรง)
2. ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (คูณ 1.2 บนผลข้อ 1)
3. ส่งด่วน คิดเพิ่ม 50% (คูณ 1.5 คูณต่อจากข้อ 2)
4. ปัดลงเป็นจำนวนเต็มสตางค์ ครั้งเดียวที่ขั้นสุดท้าย (โจทย์ไม่ระบุโหมดปัด จึงใช้ปัดลง)
"""

from fractions import Fraction
import math


def _to_fraction(value):
    # float ใช้ str() เพื่อให้ได้ทศนิยมตามที่เขียน (เช่น 100.1 -> 1001/10) ไม่หลุดจาก binary float
    if isinstance(value, float):
        return Fraction(str(value))
    return Fraction(value)


def _base_fee_baht(weight_g):
    """ค่าส่งฐานตามน้ำหนัก (บาท) รับ weight_g เป็น Fraction"""
    if weight_g <= 1000:
        return Fraction(40)
    if weight_g <= 5000:
        return Fraction(80)
    # เกิน 5,000 กรัม: 80 บาท + ส่วนที่เกินคิดตามสัดส่วนกรัม กิโลกรัมละ 15 บาท
    return Fraction(80) + (weight_g - 5000) / 1000 * 15


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (int)

    weight_g    : น้ำหนัก 1–30,000 กรัม
    distance_km : ระยะทาง (ตั้งแต่ 0 กม.)
    express     : True = ส่งด่วน
    """
    w = _to_fraction(weight_g)
    d = _to_fraction(distance_km)

    if not (1 <= w <= 30000):
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1–30,000 กรัม")
    if d < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    fee = _base_fee_baht(w)            # ข้อ 1
    if d > 100:                        # ข้อ 2: เกิน 100 กม. (ไม่รวมที่พอดี 100)
        fee *= Fraction(120, 100)
    if express:                        # ข้อ 3: คูณต่อจากข้อ 2
        fee *= Fraction(150, 100)

    return math.floor(fee * 100)       # ข้อ 4: บาท -> สตางค์ แล้วปัดลงครั้งเดียว
