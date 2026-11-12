"""BaanKafe bulk coffee-bean pricing.

ราคาทั้งหมดเป็นสตางค์ (satang) จำนวนเต็ม ผลลัพธ์ก็เป็นจำนวนเต็มสตางค์เช่นกัน
"""

from fractions import Fraction
from decimal import Decimal, ROUND_HALF_UP

BULK_TIER_50 = Fraction(75, 1000)   # 7.5% เมื่อซื้อ 50 ถุงขึ้นไป
BULK_TIER_10 = Fraction(35, 1000)   # 3.5% เมื่อซื้อ 10 ถุงขึ้นไป
COUPON_RATE = Fraction(25, 1000)    # 2.5% เมื่อมีคูปอง (ลดต่อจากส่วนลดขายส่ง)
VAT_RATE = Fraction(7, 100)         # VAT 7% ขั้นสุดท้าย

MIN_QTY = 1
MAX_QTY = 1000


def _bulk_rate(qty: int) -> Fraction:
    """อัตราลดขายส่ง ใช้อัตราเดียวตามจำนวนถุงที่สูงสุดที่เข้าเงื่อนไข"""
    if qty >= 50:
        return BULK_TIER_50
    if qty >= 10:
        return BULK_TIER_10
    return Fraction(0)


def _round_satang(amount: Fraction) -> int:
    """ปัดเศษเป็นจำนวนเต็มสตางค์ (ปัดขึ้นเมื่อ .5 พอดี)"""
    value = Decimal(amount.numerator) / Decimal(amount.denominator)
    return int(value.quantize(Decimal(1), rounding=ROUND_HALF_UP))


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
    """คืนยอดที่ลูกค้าต้องจ่าย (สตางค์, จำนวนเต็ม)

    unit_price: ราคาต่อถุง (สตางค์, >= 0)
    qty:        จำนวนถุง (1–1000)
    coupon:     True ถ้ามีคูปอง
    """
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise TypeError("unit_price ต้องเป็นจำนวนเต็ม (สตางค์)")
    if unit_price < 0:
        raise ValueError("unit_price ต้องไม่ติดลบ")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise TypeError("qty ต้องเป็นจำนวนเต็ม")
    if not MIN_QTY <= qty <= MAX_QTY:
        raise ValueError(f"qty ต้องอยู่ระหว่าง {MIN_QTY}–{MAX_QTY}")
    if not isinstance(coupon, bool):
        raise TypeError("coupon ต้องเป็น True หรือ False")

    # คำนวณด้วยเศษส่วนที่แม่นยำ ปัดเศษครั้งเดียวที่ท้ายสุด
    total = Fraction(unit_price * qty)
    total *= 1 - _bulk_rate(qty)
    if coupon:
        total *= 1 - COUPON_RATE
    total *= 1 + VAT_RATE

    return _round_satang(total)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน (ราคาถุงละ 25,000 สตางค์ = 250 บาท)
    print(bulk_price(25000, 1, False))    # 25000 * 1.07 = 26750
    print(bulk_price(25000, 10, False))   # 250000 * 0.965 * 1.07
    print(bulk_price(25000, 50, True))    # 1250000 * 0.925 * 0.975 * 1.07
