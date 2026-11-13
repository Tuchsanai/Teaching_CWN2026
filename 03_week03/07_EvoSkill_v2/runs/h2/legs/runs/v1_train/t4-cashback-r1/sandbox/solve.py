"""BaanKafe cashback calculator.

หน่วยทั้งหมดเป็นสตางค์ (1 บาท = 100 สตางค์) ผลลัพธ์เป็นจำนวนเต็มสตางค์

กติกาตามลำดับในโจทย์:
1. อัตราเงินคืนตามระดับสมาชิก: silver 1.5%, gold 2.5%, platinum 4%
2. ยอดซื้อต่ำกว่า 100 บาท (10000 สตางค์) ไม่ได้เงินคืน
3. ซื้อในเดือนเกิด (birthday=True) ได้เงินคืน 2 เท่า
4. เงินคืนสูงสุด 200 บาทต่อบิล (20000 สตางค์) คิดหลังคูณ 2 เท่าแล้ว
5. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ครั้งเดียวที่ผลลัพธ์
"""

import math
from fractions import Fraction

RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(40, 1000),  # 4%
}

MIN_AMOUNT = 10000   # 100 บาท ในหน่วยสตางค์
BIRTHDAY_MULTIPLIER = 2
MAX_CASHBACK = 20000  # 200 บาท ในหน่วยสตางค์


def _to_frac(x):
    """แปลงตัวเลขเป็น Fraction ผ่าน str เพื่อไม่ให้เกิดคลาดเคลื่อนจาก float"""
    return Fraction(str(x))


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ยอดไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def cashback(amount, tier, birthday):
    """คืนค่าเงินคืนเป็นจำนวนเต็มสตางค์

    amount: ยอดซื้อ (สตางค์, ตั้งแต่ 0)
    tier: "silver" | "gold" | "platinum"
    birthday: True ถ้าซื้อในเดือนเกิด
    """
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise ValueError("amount ต้องเป็นตัวเลข")
    amt = _to_frac(amount)
    if amt < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    key = tier.strip().lower() if isinstance(tier, str) else tier
    if key not in RATES:
        raise ValueError(f"tier ไม่รู้จัก: {tier!r}")

    # ข้อ 2: ยอดต่ำกว่า 100 บาท ไม่ได้เงินคืน
    if amt < MIN_AMOUNT:
        return 0

    # ข้อ 1 และ 3: อัตรา แล้วคูณ 2 เท่าถ้าเป็นเดือนเกิด
    raw = amt * RATES[key]
    if birthday:
        raw *= BIRTHDAY_MULTIPLIER

    # ข้อ 4: เพดานหลังคูณทุกตัวแล้ว
    capped = min(raw, Fraction(MAX_CASHBACK))

    # ข้อ 5: ปัดครั้งเดียวตอนคืนค่า
    return _round_half_up(capped)


def _run_tests():
    cases = [
        # (amount, tier, birthday, expected)
        (0, "silver", False, 0),
        (9999, "platinum", True, 0),          # ต่ำกว่า 100 บาท ไม่ได้เงินคืน
        (10000, "silver", False, 150),        # 100 บาท × 1.5% = 1.5 บาท
        (10000, "gold", False, 250),          # 100 บาท × 2.5% = 2.5 บาท
        (10000, "platinum", False, 400),      # 100 บาท × 4% = 4 บาท
        (10000, "silver", True, 300),         # เดือนเกิด 2 เท่า
        (10100, "silver", False, 152),        # 151.5 สตางค์ ปัดครึ่งขึ้นเป็น 152
        (10300, "silver", False, 155),        # 154.5 สตางค์ ปัดครึ่งขึ้นเป็น 155
        (1000000, "platinum", False, 20000),  # 10000 บาท × 4% = 400 บาท เกินเพดาน 200
        (1000000, "gold", True, 20000),       # 250 × 2 = 500 บาท เกินเพดาน 200
        (1000000, "silver", False, 15000),    # 10000 บาท × 1.5% = 150 บาท ยังไม่ถึงเพดาน
        (1000000, "silver", True, 20000),     # 150 × 2 = 300 บาท เกินเพดาน 200
        (10000.0, "gold", False, 250),        # float ที่เป็นจำนวนเต็มรับได้
    ]

    for amount, tier, birthday, expected in cases:
        got = cashback(amount, tier, birthday)
        assert got == expected, (amount, tier, birthday, got, expected)

    for bad in [(-1, "silver", False), (10000, "diamond", False), (True, "gold", False)]:
        try:
            cashback(*bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"ควร raise ValueError: {bad}")

    print(f"ผ่านทั้งหมด {len(cases)} กรณี + ตรวจอินพุตผิดได้ถูกต้อง")


if __name__ == "__main__":
    _run_tests()
