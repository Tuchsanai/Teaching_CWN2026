"""BaanKafe bulk price calculator.

ราคาทั้งหมดคิดเป็นสตางค์ (integer) และใช้ Fraction ตลอดการคำนวณกลาง
เพื่อไม่ให้เกิดความคลาดเคลื่อนจาก float จากนั้นปัดเศษเป็นจำนวนเต็มสตางค์
แบบ ROUND_HALF_UP เป็นขั้นสุดท้าย

ลำดับการคิดลด:
1. ส่วนลดตามจำนวน (ใช้อัตราเดียว): 50 ถุงขึ้นไป 7.5%, 10 ถุงขึ้นไป 3.5%
2. ส่วนลดคูปอง 2.5% (ลดต่อจากยอดหลังส่วนลดข้อ 1)
3. VAT 7% (บวกเป็นขั้นสุดท้าย)
"""

from fractions import Fraction

VAT_RATE = Fraction(7, 100)
COUPON_RATE = Fraction(5, 200)  # 2.5%

# (จำนวนถุงขั้นต่ำ, อัตราส่วนลด) เรียงจากมากไปน้อย ใช้อัตราแรกที่เข้าเงื่อนไข
VOLUME_TIERS = (
    (50, Fraction(15, 200)),  # 7.5%
    (10, Fraction(7, 200)),   # 3.5%
)


def _volume_rate(qty: int) -> Fraction:
    for min_qty, rate in VOLUME_TIERS:
        if qty >= min_qty:
            return rate
    return Fraction(0)


def _round_half_up(value: Fraction) -> int:
    """ปัดค่าที่ไม่ติดลบให้เป็นจำนวนเต็ม (0.5 ปัดขึ้น)."""
    return int(value + Fraction(1, 2))


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
    """คืนยอดที่ลูกค้าต้องจ่าย (สตางค์, จำนวนเต็ม)

    unit_price: ราคาต่อถุง หน่วยสตางค์ (>= 0)
    qty:        จำนวนถุง (1–1000)
    coupon:     True ถ้ามีคูปอง
    """
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise TypeError("unit_price must be an int (satang)")
    if unit_price < 0:
        raise ValueError("unit_price must be >= 0")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise TypeError("qty must be an int")
    if not 1 <= qty <= 1000:
        raise ValueError("qty must be between 1 and 1000")
    if not isinstance(coupon, bool):
        raise TypeError("coupon must be a bool")

    total = Fraction(unit_price * qty)

    # 1) ส่วนลดตามจำนวน
    total *= 1 - _volume_rate(qty)

    # 2) ส่วนลดคูปอง
    if coupon:
        total *= 1 - COUPON_RATE

    # 3) VAT 7% เป็นขั้นสุดท้าย
    total *= 1 + VAT_RATE

    return _round_half_up(total)


if __name__ == "__main__":
    print(bulk_price(10000, 1, False))   # 100 บาท ไม่ลด + VAT -> 10700
    print(bulk_price(10000, 10, False))  # ลด 3.5% + VAT -> 103255
    print(bulk_price(10000, 50, True))   # ลด 7.5% + คูปอง 2.5% + VAT -> 482503
