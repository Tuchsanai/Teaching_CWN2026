"""ค่าส่งเมล็ดกาแฟ BaanKafe

shipping_fee(weight_g, distance_km, express) -> int (สตางค์)
"""
import math
from fractions import Fraction


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int, x ไม่ติดลบ (ค่าส่งเป็นเงินที่ลูกค้าจ่ายให้ร้าน)"""
    return int((Fraction(x) * 2 + 1) // 2)


def _require_int(value, name, low, high):
    if type(value) is not int:  # ปฏิเสธ bool, float, str, None
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if not (low <= value <= high):
        raise ValueError(f"{name} ต้องอยู่ระหว่าง {low} ถึง {high}")
    return value


def _require_distance(value):
    if type(value) not in (int, float):  # ปฏิเสธ bool, str, None
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("distance_km ต้องเป็นตัวเลขจำกัด")
    if value < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")
    return value


def _require_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def _base_satang(weight_g):
    """ค่าส่งฐานตามน้ำหนัก เป็นสตางค์ (Fraction ยังไม่ปัด)"""
    if weight_g <= 1_000:
        return Fraction(40 * 100)
    if weight_g <= 5_000:
        return Fraction(80 * 100)
    # เกิน 5,000 กรัม: 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน (คิดตามสัดส่วนกรัม)
    extra_g = weight_g - 5_000
    return Fraction(80 * 100) + Fraction(extra_g * 15 * 100, 1_000)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : int 1–30,000 กรัม
    distance_km : ตัวเลขตั้งแต่ 0 (กม.)
    express     : bool, True = ส่งด่วน
    """
    weight_g = _require_int(weight_g, "weight_g", 1, 30_000)
    distance_km = _require_distance(distance_km)
    express = _require_bool(express, "express")

    fee = _base_satang(weight_g)

    # ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if distance_km > 100:
        fee *= Fraction(6, 5)

    # ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
    if express:
        fee *= Fraction(3, 2)

    # ปัดครั้งเดียวตอนท้ายสุด
    return _half_up(fee)


if __name__ == "__main__":
    print(shipping_fee(500, 10, False))     # 4000
    print(shipping_fee(5_000, 100, False))  # 8000
    print(shipping_fee(5_001, 101, True))   # 14403
