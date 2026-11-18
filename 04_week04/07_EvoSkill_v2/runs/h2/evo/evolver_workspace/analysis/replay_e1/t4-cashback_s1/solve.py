"""BaanKafe: คิดเงินคืนสมาชิก

cashback(amount, tier, birthday)
- amount   : ยอดซื้อ หน่วยสตางค์ (จำนวนเต็ม >= 0)
- tier     : "silver" | "gold" | "platinum" (ตรงตัวอักษร)
- birthday : True = ซื้อในเดือนเกิด, False = ไม่ใช่

กติกา
1. อัตราเงินคืน: silver 1.5%, gold 2.5%, platinum 4%
2. ยอดซื้อต่ำกว่า 100 บาท (10000 สตางค์) ไม่ได้เงินคืน
3. เดือนเกิด ได้เงินคืน 2 เท่า
4. เงินคืนสูงสุด 200 บาท (20000 สตางค์) ต่อบิล
5. ผลลัพธ์เป็นจำนวนเต็มสตางค์

การปัด (ไม่ได้ระบุในโจทย์): เงินที่ร้านจ่ายคืนให้ลูกค้า จึงปัดลง
ลำดับ: คูณอัตรา (ยังไม่ปัด) -> คูณ 2 ถ้าเดือนเกิด -> เพดาน -> ปัดลงครั้งเดียว
"""

import math
from fractions import Fraction

# อัตราเงินคืนแบบ exact (1.5% = 3/200 ฯลฯ)
RATES = {
    "silver": Fraction(3, 200),
    "gold": Fraction(1, 40),
    "platinum": Fraction(1, 25),
}

MIN_AMOUNT_SATANG = 10_000   # 100 บาท
MAX_CASHBACK_SATANG = 20_000  # 200 บาท
BIRTHDAY_MULTIPLIER = 2


def _need_int(value, name, low=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    return value


def _need_bool(value, name):
    """flag: ต้องเป็น True หรือ False จริง"""
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def _need_choice(value, name, choices):
    """string ที่ต้องตรงตัวเลือกเป๊ะ (ไม่ strip, ไม่ lower)"""
    if type(value) is not str or value not in choices:
        raise ValueError(f"{name} ต้องเป็นหนึ่งใน {sorted(choices)}")
    return value


def cashback(amount, tier, birthday):
    """คืนเงินคืนเป็นจำนวนเต็มสตางค์ ตามกติกาของ BaanKafe"""
    _need_int(amount, "amount", low=0)
    _need_choice(tier, "tier", RATES.keys())
    _need_bool(birthday, "birthday")

    if amount < MIN_AMOUNT_SATANG:
        return 0

    value = Fraction(amount) * RATES[tier]          # ยังไม่ปัด
    if birthday:
        value *= BIRTHDAY_MULTIPLIER                # ยังไม่ปัด
    value = min(value, MAX_CASHBACK_SATANG)         # เพดาน
    return math.floor(value)                        # ปัดลงครั้งเดียว


if __name__ == "__main__":
    examples = [
        (10_000, "silver", False),   # 150
        (10_000, "gold", True),      # 500
        (10_000, "platinum", True),  # 800
        (9_999, "platinum", True),   # 0 (ต่ำกว่า 100 บาท)
        (1_000_000, "platinum", False),  # 20000 (เพดาน)
    ]
    for amount, tier, birthday in examples:
        print(amount, tier, birthday, "->", cashback(amount, tier, birthday))
