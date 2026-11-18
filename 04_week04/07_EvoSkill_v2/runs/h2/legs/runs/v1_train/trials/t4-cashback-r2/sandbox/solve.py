"""BaanKafe: คิดเงินคืนสมาชิก

หน่วย: amount และผลลัพธ์เป็นสตางค์ (จำนวนเต็ม)

ลำดับการคิด (ปัดครั้งเดียวตอนท้าย):
1. ยอดต่ำกว่า 100 บาท (10000 สตางค์) -> 0
2. amount * อัตราตามระดับ (silver 1.5%, gold 2.5%, platinum 4%) แบบ Fraction
3. เดือนเกิด (birthday=True) -> คูณ 2
4. เพดานสูงสุด 200 บาท (20000 สตางค์) ต่อบิล
5. ปัดลงเป็นจำนวนเต็มสตางค์ (ร้านเป็นผู้จ่ายเงินคืน จึงไม่ปัดขึ้นเกินจริง)
"""

import math
from fractions import Fraction


# ---------- ตรวจข้อมูลนำเข้า (ผิดชนิดหรือนอกช่วง -> ValueError) ----------

def _need_int(value, name, low=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    return value


def _need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def _need_choice(value, name, choices):
    if type(value) is not str or value not in choices:
        raise ValueError(f"{name} ต้องเป็นหนึ่งใน {sorted(choices)}")
    return value


# ---------- ค่าคงที่ของโจทย์ ----------

RATES = {
    "silver": Fraction(15, 1000),   # 1.5%
    "gold": Fraction(25, 1000),     # 2.5%
    "platinum": Fraction(4, 100),   # 4%
}
MIN_PURCHASE = 100 * 100            # 100 บาท ในหน่วยสตางค์
BIRTHDAY_MULTIPLIER = 2
MAX_CASHBACK = 200 * 100            # 200 บาท ต่อบิล ในหน่วยสตางค์


def cashback(amount, tier, birthday):
    """คืนค่าเงินคืนเป็นจำนวนเต็มสตางค์"""
    _need_int(amount, "amount", low=0)
    _need_choice(tier, "tier", set(RATES))
    _need_bool(birthday, "birthday")

    if amount < MIN_PURCHASE:
        return 0

    value = Fraction(amount) * RATES[tier]
    if birthday:
        value *= BIRTHDAY_MULTIPLIER
    value = min(value, Fraction(MAX_CASHBACK))
    return math.floor(value)


if __name__ == "__main__":
    print("silver 100 บาท:", cashback(10000, "silver", False))   # 150
    print("gold 1,000 บาท:", cashback(100000, "gold", False))    # 2500
    print("platinum 5,000 บาท:", cashback(500000, "platinum", False))  # 20000 (เพดาน)
    print("gold เดือนเกิด 1,000 บาท:", cashback(100000, "gold", True))  # 5000
