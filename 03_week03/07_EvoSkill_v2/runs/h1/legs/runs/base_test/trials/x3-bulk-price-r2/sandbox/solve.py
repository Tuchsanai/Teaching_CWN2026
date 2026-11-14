"""BaanKafe bulk coffee-bean pricing.

ราคาทั้งหมดคิดเป็นสตางค์ (จำนวนเต็ม) และใช้เลขตรรกยะ (Fraction) ระหว่างคำนวณ
เพื่อไม่ให้เกิดความคลาดเคลื่อนของทศนิยมแบบ float
"""

from fractions import Fraction
from math import floor


def _bulk_rate(qty: int) -> Fraction:
    """อัตราส่วนลดตามจำนวนถุง (ใช้อัตราเดียว ไม่สะสมกัน)."""
    if qty >= 50:
        return Fraction(75, 1000)  # 7.5%
    if qty >= 10:
        return Fraction(35, 1000)  # 3.5%
    return Fraction(0)


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นสตางค์ (จำนวนเต็ม ปัดเศษแบบ half-up).

    ขั้นตอน:
      1. ราคารวม = unit_price * qty
      2. ลดตามปริมาณ: 10+ ถุง 3.5%, 50+ ถุง 7.5% (อัตราเดียว)
      3. ถ้ามีคูปอง ลดอีก 2.5% (คิดต่อจากยอดหลังขั้นที่ 2)
      4. บวก VAT 7% เป็นขั้นสุดท้าย
      5. ปัดเศษเป็นสตางค์จำนวนเต็ม (half-up)

    Args:
        unit_price: ราคาต่อถุง หน่วยสตางค์ (>= 0)
        qty: จำนวนถุง (1–1000)
        coupon: True ถ้ามีคูปอง

    Raises:
        TypeError: ถ้า unit_price หรือ qty ไม่ใช่ int (หรือ coupon ไม่ใช่ bool)
        ValueError: ถ้า unit_price < 0 หรือ qty อยู่นอกช่วง 1–1000
    """
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise TypeError("unit_price must be an int (satang)")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise TypeError("qty must be an int")
    if not isinstance(coupon, bool):
        raise TypeError("coupon must be a bool")
    if unit_price < 0:
        raise ValueError("unit_price must be >= 0")
    if not 1 <= qty <= 1000:
        raise ValueError("qty must be between 1 and 1000")

    total = Fraction(unit_price * qty)
    total *= 1 - _bulk_rate(qty)
    if coupon:
        total *= Fraction(975, 1000)  # ลด 2.5%
    total *= Fraction(107, 100)  # VAT 7%

    # ปัดเศษแบบ half-up ไปเป็นสตางค์จำนวนเต็ม
    return floor(total + Fraction(1, 2))


if __name__ == "__main__":
    # ตัวอย่างการใช้งานเบื้องต้น
    print(bulk_price(20000, 1, False))   # 200 บาท 1 ถุง -> 21400 สตางค์ (214.00 บาท)
    print(bulk_price(20000, 10, False))  # ลด 3.5%
    print(bulk_price(20000, 50, True))   # ลด 7.5% + คูปอง 2.5%
