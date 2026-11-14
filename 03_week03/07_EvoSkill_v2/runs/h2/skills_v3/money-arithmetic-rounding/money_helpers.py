"""ตัวช่วยคำนวณเงินและตรวจข้อมูลนำเข้า

ไม่มี side effect ตอน import. วิธีใช้: คัดลอกฟังก์ชันที่ต้องใช้ไปไว้ใน solve.py
(ปลอดภัยที่สุด เพราะไม่ต้องพึ่ง sys.path) หรือ import จากไฟล์นี้ถ้าอยู่โฟลเดอร์เดียวกัน

หลักการ: ผิดชนิดหรือนอกช่วง -> ValueError เท่านั้น (ไม่ใช้ TypeError)
"""

import math
from fractions import Fraction


# ---------- ตรวจข้อมูลนำเข้า ----------

def need_int(value, name, low=None, high=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


def need_bool(value, name):
    """flag: ต้องเป็น True หรือ False จริง"""
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def need_choice(value, name, choices):
    """ค่า string ที่ต้องตรงตัวเลือกเป๊ะ (ไม่ strip, ไม่ lower)"""
    if type(value) is not str or value not in choices:
        raise ValueError(f"{name} ต้องเป็นหนึ่งใน {sorted(choices)}")
    return value


def need_number(value, name, low=None):
    """ตัวเลขที่ไม่ใช่ bool: รับ int หรือ float แล้วแปลงเป็น Fraction ผ่าน str
    (str(float) คืนทศนิยมสั้นที่ตรงกับที่ผู้ใช้พิมพ์ จึงไม่เกิดความคลาดเคลื่อนแบบ binary)
    ถ้าโจทย์ระบุว่าต้องเป็นจำนวนเต็ม ให้ใช้ need_int แทน
    """
    if type(value) not in (int, float):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    try:
        x = Fraction(str(value))
    except (ValueError, OverflowError) as exc:  # เช่น nan, inf
        raise ValueError(f"{name} ไม่ใช่ตัวเลขที่ใช้ได้") from exc
    if low is not None and x < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    return x


# ---------- ปัดเศษ (ปัดครั้งเดียวตอนท้ายเสมอ) ----------

def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


def round_down(x):
    """ปัดลงเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.9 -> 2"""
    return math.floor(Fraction(x))


# ---------- เปอร์เซ็นต์ ----------

def percent(amount, pct):
    """amount * pct / 100 แบบ exact ยังไม่ปัด.
    pct ส่งเป็น int หรือ str เช่น '1.5' (อย่าส่ง float เช่น 0.015)
    """
    return Fraction(amount) * Fraction(pct) / 100


# ---------- การหารให้ครบ ----------

def split_even(total, people):
    """หาร total (จำนวนเต็ม) ให้ people คน เศษให้คนลำดับต้น ๆ คนละ 1 หน่วยตามลำดับ"""
    base, rem = divmod(total, people)
    return [base + 1] * rem + [base] * (people - rem)


if __name__ == "__main__":
    # self-check เล็ก ๆ ของตัวช่วย
    assert half_up(Fraction(5, 2)) == 3
    assert half_up(Fraction(12, 5)) == 2
    assert round_down(Fraction(5, 2)) == 2
    assert percent(10000, "1.5") == Fraction(150)
    assert split_even(10000, 3) == [3334, 3333, 3333]
    assert split_even(2, 3) == [1, 1, 0]
    assert sum(split_even(12345, 7)) == 12345
    print("money_helpers ok")
