"""BaanKafe bulk coffee-bean pricing.

ราคาทั้งหมดคิดเป็นสตางค์ (จำนวนเต็ม) และใช้ Fraction เพื่อไม่ให้มีค่าคลาดเคลื่อนจากทศนิยม
ผลสุดท้ายปัดเศษแบบครึ่งขึ้น (ROUND_HALF_UP) ให้เป็นจำนวนเต็มสตางค์
"""

from fractions import Fraction

VAT_RATE = Fraction(7, 100)          # VAT 7% (ขั้นสุดท้าย)
COUPON_RATE = Fraction(25, 1000)     # คูปองลด 2.5% (ลดต่อจากส่วนลดจำนวน)
TIER_50_RATE = Fraction(75, 1000)    # ซื้อ 50 ถุงขึ้นไป ลด 7.5%
TIER_10_RATE = Fraction(35, 1000)    # ซื้อ 10 ถุงขึ้นไป ลด 3.5%

MIN_QTY = 1
MAX_QTY = 1000


def _volume_rate(qty: int) -> Fraction:
    """อัตราส่วนลดตามจำนวน (ใช้อัตราเดียวตามขั้นสูงสุดที่เข้าเงื่อนไข)."""
    if qty >= 50:
        return TIER_50_RATE
    if qty >= 10:
        return TIER_10_RATE
    return Fraction(0)


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์.

    unit_price: ราคาต่อถุง (สตางค์, >= 0)
    qty:        จำนวนถุง (1–1000)
    coupon:     True = มีคูปอง ลดเพิ่ม 2.5%
    """
    # ตรวจสอบอินพุต (bool เป็น subclass ของ int จึงต้องกันไว้ด้วย)
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

    subtotal = Fraction(unit_price * qty)

    # 1) ส่วนลดตามจำนวน
    after_volume = subtotal * (1 - _volume_rate(qty))

    # 2) ส่วนลดคูปอง (ถ้ามี) คิดจากยอดหลังลดขั้นแรก
    if coupon:
        after_coupon = after_volume * (1 - COUPON_RATE)
    else:
        after_coupon = after_volume

    # 3) VAT 7% เป็นขั้นสุดท้าย
    total = after_coupon * (1 + VAT_RATE)

    # ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (total >= 0 เสมอ)
    return int(total + Fraction(1, 2))


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน (ราคาถุงละ 250.00 บาท = 25000 สตางค์)
    examples = [
        (25000, 1, False),
        (25000, 10, False),
        (25000, 10, True),
        (25000, 50, False),
        (25000, 50, True),
        (25000, 1000, True),
    ]
    for unit, qty, cp in examples:
        print(f"unit={unit} qty={qty} coupon={cp} -> {bulk_price(unit, qty, cp)} สตางค์")
