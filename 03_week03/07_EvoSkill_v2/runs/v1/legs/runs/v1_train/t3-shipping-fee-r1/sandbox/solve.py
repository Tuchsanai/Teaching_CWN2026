import math
from fractions import Fraction

EXPRESS_MAX_G = 20000  # สมมติฐาน: ส่งด่วนรับสูงสุด 20,000 กรัม (เกินให้ ValueError)


def _need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    _need_int(weight_g, "weight_g", 1, 30000)
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

    # สมมติฐาน: ระยะ 0 กม. = รับเองที่ร้าน ค่าส่ง 0
    if distance_km == 0:
        return 0

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + Fraction(1500 * (weight_g - 5000), 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return int((fee * 2 + 1) // 2)  # ปัดครึ่งขึ้นครั้งเดียว
