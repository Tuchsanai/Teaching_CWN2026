"""BaanKafe cashback calculator.

หน่วยทั้งหมดเป็นสตางค์ (1 บาท = 100 สตางค์) คำนวณด้วย Fraction ทั้งหมด
และปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์เพียงครั้งเดียวที่ขั้นสุดท้าย

ลำดับการคิด:
1. ยอดซื้อต่ำกว่า 100 บาท (10,000 สตางค์) -> ไม่ได้เงินคืน (0)
2. เงินคืนพื้นฐาน = ยอดซื้อ × อัตราของระดับสมาชิก
3. ถ้าซื้อในเดือนเกิด -> คูณ 2
4. เพดานสูงสุด 200 บาท (20,000 สตางค์) ต่อบิล ตัดที่ขั้นสุดท้าย
5. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์

การตีความที่เลือก (กำกวมในโจทย์):
- ปัดครึ่งขึ้น (ค่าเริ่มต้นของการปัดเงินในงานนี้) ถ้าต้องการปัดลง เปลี่ยน
  `_round_half_up` ให้คืน `math.floor(x)`
- เกณฑ์ 100 บาท ตรวจกับยอดซื้อก่อนคิดเงินคืน (ยอด 100 บาทพอดีได้เงินคืน)
"""

from fractions import Fraction
import math

MIN_AMOUNT_SATANG = 100 * 100        # 100 บาท
MAX_CASHBACK_SATANG = 200 * 100      # 200 บาทต่อบิล

# อัตราเงินคืนเป็นเปอร์เซ็นต์ (Fraction เพื่อไม่ให้มี float ปน)
RATES_PERCENT = {
    "silver": Fraction(15, 10),      # 1.5%
    "gold": Fraction(25, 10),        # 2.5%
    "platinum": Fraction(4),         # 4%
}


def _round_half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ใช้กับค่าไม่ติดลบ)"""
    return math.floor(Fraction(x) + Fraction(1, 2))


def cashback(amount, tier, birthday):
    """คืนค่าเงินคืนเป็นจำนวนเต็มสตางค์

    amount   : ยอดซื้อเป็นสตางค์ (int, >= 0)
    tier     : "silver", "gold" หรือ "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if tier not in RATES_PERCENT:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r}")

    # 1. เกณฑ์ขั้นต่ำ ตรวจกับยอดซื้อ
    if amount < MIN_AMOUNT_SATANG:
        return 0

    # 2. เงินคืนพื้นฐาน
    base = Fraction(amount) * RATES_PERCENT[tier] / 100

    # 3. เดือนเกิดได้ 2 เท่า
    if birthday:
        base *= 2

    # 4. เพดานต่อบิล ตัดที่ขั้นสุดท้าย แล้วค่อยปัด
    capped = min(base, Fraction(MAX_CASHBACK_SATANG))

    # 5. ปัดครั้งเดียวที่ขั้นสุดท้าย
    return int(_round_half_up(capped))


if __name__ == "__main__":
    examples = [
        (10_000, "silver", False),
        (100_000, "gold", False),
        (50_000, "platinum", True),
        (99_999, "gold", True),
        (500_000, "platinum", False),
    ]
    for amt, t, b in examples:
        print(f"amount={amt:>7} tier={t:<8} birthday={b!s:<5} -> cashback={cashback(amt, t, b)} satang")
