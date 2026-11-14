from fractions import Fraction


def _need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def _need_bool(v, name):
    if type(v) is not bool:
        raise ValueError(f"{name} ต้องเป็น True/False")
    return v


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้นครั้งเดียวตอนจบ)

    สมมติฐาน (โจทย์ไม่ได้ระบุ):
    - ระยะทาง 0 กม. = ลูกค้ารับเองที่ร้าน -> ค่าส่ง 0
    - ส่งด่วนรับน้ำหนักสูงสุด 20,000 กรัม เกินนั้น ValueError
    - distance_km ต้องเป็นจำนวนเต็ม
    """
    _need_int(weight_g, "weight_g", 1, 30000)
    _need_int(distance_km, "distance_km", 0)
    _need_bool(express, "express")
    if express and weight_g > 20000:
        raise ValueError("ส่งด่วนรับไม่เกิน 20,000 กรัม")
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
    return int((fee * 2 + 1) // 2)
