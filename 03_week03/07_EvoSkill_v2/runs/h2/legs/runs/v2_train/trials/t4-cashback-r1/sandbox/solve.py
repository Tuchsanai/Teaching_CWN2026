"""BaanKafe: คิดเงินคืนสมาชิก

cashback(amount, tier, birthday) -> จำนวนเงินคืนเป็นสตางค์ (จำนวนเต็ม)

กฎ:
1. amount = ยอดซื้อเป็นสตางค์ (จำนวนเต็ม >= 0)
2. tier = "silver" | "gold" | "platinum" (ตรงตัวอักษร)
3. birthday = True ถ้าซื้อในเดือนเกิด
4. อัตรา: silver 1.5%, gold 2.5%, platinum 4%
5. ยอดซื้อต่ำกว่า 100 บาท (10000 สตางค์) ไม่ได้เงินคืน (คืน 0)
6. เดือนเกิดได้เงินคืน 2 เท่า
7. เงินคืนสูงสุด 200 บาท (20000 สตางค์) ต่อบิล
8. คืนเป็นจำนวนเต็มสตางค์ ปัดลง (ร้านจ่ายออก ไม่จ่ายเกิน)

ลำดับการคำนวณ: ตรวจ input -> เกณฑ์ขั้นต่ำ -> คูณอัตรา (exact)
-> ×2 เดือนเกิด -> เพดาน 200 บาท -> ปัดลงครั้งเดียว

ไม่มี side effect ตอน import
"""

import math
from fractions import Fraction

MIN_AMOUNT = 10000  # 100 บาท เป็นสตางค์
CAP = 20000  # 200 บาท เป็นสตางค์
RATES = {
    "silver": Fraction(15, 1000),  # 1.5%
    "gold": Fraction(25, 1000),  # 2.5%
    "platinum": Fraction(4, 100),  # 4%
}


# ---------- ตรวจข้อมูลนำเข้า (ผิดชนิดหรือนอกช่วง -> ValueError เท่านั้น) ----------


def need_int(value, name, low=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    return value


def need_bool(value, name):
    """flag: ต้องเป็น True หรือ False จริง"""
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def need_choice(value, name, choices):
    """string ที่ต้องตรงตัวเลือกเป๊ะ (ไม่ strip, ไม่ lower)"""
    if type(value) is not str or value not in choices:
        raise ValueError(f"{name} ต้องเป็นหนึ่งใน {sorted(choices)}")
    return value


# ---------- ฟังก์ชันหลัก ----------


def cashback(amount, tier, birthday):
    """คืนเงินคืนเป็นสตางค์ (จำนวนเต็ม)"""
    # ตรวจ input ทั้งหมดก่อนเงื่อนไขธุรกิจ เพื่อให้ค่าผิดไม่คืน 0 เงียบ ๆ
    need_int(amount, "amount", low=0)
    need_choice(tier, "tier", RATES)
    need_bool(birthday, "birthday")

    if amount < MIN_AMOUNT:
        return 0

    back = Fraction(amount) * RATES[tier]  # exact ยังไม่ปัด
    if birthday:
        back *= 2
    back = min(back, CAP)
    return math.floor(back)  # ปัดลงครั้งเดียวตอนท้าย


if __name__ == "__main__":
    assert cashback(10000, "silver", False) == 150
    assert cashback(10000, "gold", True) == 500
    assert cashback(10030, "gold", True) == 501  # 501.5 -> 501
    assert cashback(500000, "platinum", True) == 20000  # ติดเพดาน
    assert cashback(9999, "platinum", True) == 0
    print("solve ok")
    print("ตัวอย่าง: cashback(10000, 'gold', False) =", cashback(10000, "gold", False))
