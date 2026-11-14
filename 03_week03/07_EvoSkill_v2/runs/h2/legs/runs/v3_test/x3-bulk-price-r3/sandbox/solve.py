"""BaanKafe bulk coffee pricing.

หน่วยทั้งหมดเป็นสตางค์ (1 บาท = 100 สตางค์). คำนวณด้วย Fraction ทุกขั้น
แล้วปัดครั้งเดียวที่ขั้นสุดท้าย (ปัดครึ่งเข้าเลขคู่).

ลำดับการคิด:
1. ยอดตั้งต้น = unit_price × qty
2. ส่วนลดขายส่ง (อัตราเดียว ไม่ซ้อนกัน): qty >= 50 ลด 7.5%, qty >= 10 ลด 3.5%
   ยอด × (1 − rate)
3. ถ้า coupon = True ลดอีก 2.5% บนยอดที่เหลือ (ต่อเนื่องจากข้อ 2)
4. VAT 7% เป็นขั้นสุดท้าย บนยอดหลังส่วนลดทั้งหมด
5. ปัดเป็นจำนวนเต็มสตางค์ครั้งเดียว
"""

from fractions import Fraction

BULK_TIER_1_MIN_QTY = 10
BULK_TIER_1_RATE = Fraction(35, 1000)   # 3.5%
BULK_TIER_2_MIN_QTY = 50
BULK_TIER_2_RATE = Fraction(75, 1000)   # 7.5%
COUPON_RATE = Fraction(25, 1000)        # 2.5%
VAT_RATE = Fraction(7, 100)             # 7%

MIN_QTY = 1
MAX_QTY = 1000


def _bulk_rate(qty):
    """อัตราส่วนลดขายส่งตามจำนวนถุง (อัตราเดียว ไม่สะสม)."""
    if qty >= BULK_TIER_2_MIN_QTY:
        return BULK_TIER_2_RATE
    if qty >= BULK_TIER_1_MIN_QTY:
        return BULK_TIER_1_RATE
    return Fraction(0)


def _round_half_even(x):
    """ปัดครึ่งเข้าเลขคู่ (เหมือน round() ของ Fraction)."""
    return round(x)


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์.

    unit_price: ราคาต่อถุง (สตางค์, int >= 0)
    qty: จำนวนถุง (int, 1–1000)
    coupon: True ถ้ามีคูปอง
    """
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise ValueError("unit_price ต้องเป็นจำนวนเต็มสตางค์")
    if unit_price < 0:
        raise ValueError("unit_price ต้องไม่ติดลบ")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise ValueError("qty ต้องเป็นจำนวนเต็ม")
    if not (MIN_QTY <= qty <= MAX_QTY):
        raise ValueError("qty ต้องอยู่ระหว่าง 1 ถึง 1000")

    # 1. ยอดตั้งต้น (จำนวนเต็มสตางค์ ไม่มีความคลาด)
    total = Fraction(unit_price * qty)

    # 2. ส่วนลดขายส่ง
    total *= 1 - _bulk_rate(qty)

    # 3. คูปอง ลดอีก 2.5% บนยอดที่เหลือ
    if coupon:
        total *= 1 - COUPON_RATE

    # 4. VAT 7% ขั้นสุดท้าย
    total *= 1 + VAT_RATE

    # 5. ปัดครั้งเดียว
    return int(_round_half_even(total))


if __name__ == "__main__":
    examples = [
        (10000, 1, False),
        (10000, 10, False),
        (10000, 50, True),
        (0, 1000, True),
    ]
    for unit_price, qty, coupon in examples:
        print(unit_price, qty, coupon, "->", bulk_price(unit_price, qty, coupon))
