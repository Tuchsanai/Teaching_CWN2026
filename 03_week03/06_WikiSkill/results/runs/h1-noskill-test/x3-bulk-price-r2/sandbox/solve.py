"""BaanKafe bulk coffee-bean pricing.

ราคาทั้งหมดเป็นสตางค์ (จำนวนเต็ม) ผลลัพธ์เป็นจำนวนเต็มสตางค์
"""

from decimal import Decimal, ROUND_HALF_UP

VAT_RATE = Decimal("0.07")
COUPON_RATE = Decimal("0.025")


def _bulk_rate(qty: int) -> Decimal:
    """อัตราส่วนลดขายส่ง (ใช้อัตราเดียวตามจำนวนถุง)."""
    if qty >= 50:
        return Decimal("0.075")
    if qty >= 10:
        return Decimal("0.035")
    return Decimal("0")


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์.

    - unit_price: ราคาต่อถุง (สตางค์, >= 0)
    - qty: จำนวนถุง (1–1000)
    - coupon: True = มีคูปอง ลดเพิ่มอีก 2.5% (คิดต่อจากส่วนลดขายส่ง)
    ลำดับการคิด: ยอดรวม -> ส่วนลดขายส่ง -> คูปอง -> VAT 7% (ขั้นสุดท้าย)
    """
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise TypeError("unit_price must be an int (satang)")
    if unit_price < 0:
        raise ValueError("unit_price must be >= 0")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise TypeError("qty must be an int")
    if not 1 <= qty <= 1000:
        raise ValueError("qty must be between 1 and 1000")

    total = Decimal(unit_price * qty)
    total *= Decimal("1") - _bulk_rate(qty)
    if coupon:
        total *= Decimal("1") - COUPON_RATE
    total *= Decimal("1") + VAT_RATE

    return int(total.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


if __name__ == "__main__":
    print(bulk_price(10000, 1, False))   # 100,000 * 1.07 = 10700
    print(bulk_price(10000, 10, False))  # 100,000 * 0.965 * 1.07 = 103255
    print(bulk_price(10000, 50, True))   # 500,000 * 0.925 * 0.975 * 1.07 = 482503.125 -> 482503
