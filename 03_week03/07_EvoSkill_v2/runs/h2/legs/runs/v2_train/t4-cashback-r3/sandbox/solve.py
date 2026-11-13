import math
from fractions import Fraction

# อัตราเงินคืนตามระดับสมาชิก
RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(40, 1000),  # 4%
}

MIN_AMOUNT = 100 * 100   # 100 บาท = 10000 สตางค์ (ต่ำกว่านี้ไม่ได้เงินคืน)
MAX_CASHBACK = 200 * 100  # เพดาน 200 บาท = 20000 สตางค์ต่อบิล


def _to_frac(x):
    """แปลงตัวเลขเป็น Fraction ผ่าน str เพื่อไม่ให้เกิดคลาดเคลื่อนจาก float"""
    return Fraction(str(x))


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม ใช้ครั้งเดียวตอนคืนค่า (ค่าไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def cashback(amount, tier, birthday):
    """คำนวณเงินคืนสมาชิก (หน่วยสตางค์)

    amount   : ยอดซื้อเป็นสตางค์ (>= 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด (ได้เงินคืน 2 เท่า)

    ลำดับการคิด:
      1) ยอดซื้อต่ำกว่า 100 บาท -> 0
      2) เงินคืน = ยอด x อัตราตามระดับ
      3) เดือนเกิด -> คูณ 2
      4) เพดานสูงสุด 200 บาทต่อบิล
      5) ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์
    """
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise ValueError("amount ต้องเป็นตัวเลข (สตางค์)")
    if tier not in RATES:
        raise ValueError(f"tier ไม่รู้จัก: {tier!r}")

    amt = _to_frac(amount)
    if amt < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    if amt < MIN_AMOUNT:
        return 0

    cb = amt * RATES[tier]
    if birthday:
        cb *= 2
    cb = min(cb, Fraction(MAX_CASHBACK))
    return _round_half_up(cb)


if __name__ == "__main__":
    # ตัวอย่างและกรณีขอบเขต (ค่าคำนวณด้วยมือ)
    cases = [
        ((9999, "silver", False), 0),          # ต่ำกว่า 100 บาท
        ((10000, "silver", False), 150),       # 100 บาท x 1.5%
        ((10000, "gold", False), 250),         # 100 บาท x 2.5%
        ((100000, "platinum", False), 4000),   # 1,000 บาท x 4%
        ((100000, "platinum", True), 8000),    # เดือนเกิด x2
        ((10300, "silver", False), 155),       # 154.5 สตางค์ -> ปัดครึ่งขึ้น 155
        ((500000, "platinum", False), 20000),  # ถึงเพดานพอดี
        ((1000000, "platinum", True), 20000),  # 80,000 สตางค์ -> เพดาน 20,000
        ((0, "gold", True), 0),
    ]
    for args, expected in cases:
        got = cashback(*args)
        status = "OK " if got == expected else "NG "
        print(f"{status}cashback{args} = {got} (คาดหวัง {expected})")
        assert got == expected, (args, got, expected)
    print("ผ่านทุกกรณี")
