"""BaanKafe - ฟังก์ชันหารบิล

กติกา:
1. ยอดที่ต้องหาร = ยอดบิล + ทิป (ทิป = ยอดบิล × tip_percent / 100)
2. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ครั้งเดียว ที่ยอดรวมที่ต้องหาร
3. หารเท่ากันทุกคน ถ้าไม่ลงตัว คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ
"""

import math
from decimal import Decimal
from fractions import Fraction


def _as_int(value, name, min_value=None, max_value=None):
    """แปลงค่าเป็น int ที่ถูกต้อง รับ int หรือทศนิยมที่เป็นจำนวนเต็มพอดี (เช่น 10000.0)"""
    if isinstance(value, bool):
        raise TypeError(f"{name} ต้องเป็นตัวเลข ไม่ใช่ bool")

    if isinstance(value, int):
        result = value
    elif isinstance(value, (float, Decimal, Fraction)):
        frac = Fraction(str(value)) if isinstance(value, float) else Fraction(value)
        if frac.denominator != 1:
            raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม ได้รับ {value}")
        result = int(frac)
    else:
        raise TypeError(f"{name} ต้องเป็นตัวเลข ได้รับ {type(value).__name__}")

    if min_value is not None and result < min_value:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {min_value} ได้รับ {result}")
    if max_value is not None and result > max_value:
        raise ValueError(f"{name} ต้องไม่เกิน {max_value} ได้รับ {result}")
    return result


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ยอดไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def split_bill(total, people, tip_percent):
    """หารบิลให้คนทั้งหมด คืน list ของยอดที่แต่ละคนจ่าย (สตางค์ จำนวนเต็ม) เรียงตามลำดับคน

    total        ยอดบิล (สตางค์, >= 0)
    people       จำนวนคน (>= 1)
    tip_percent  ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0-100)
    """
    total = _as_int(total, "total", min_value=0)
    people = _as_int(people, "people", min_value=1)
    tip_percent = _as_int(tip_percent, "tip_percent", min_value=0, max_value=100)

    # ยอดบิลบวกทิป คำนวณเป็นเศษส่วนให้แม่นยำ แล้วปัดครั้งเดียว
    due = _round_half_up(Fraction(total) * (100 + tip_percent) / 100)

    base, remainder = divmod(due, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    cases = [
        ((10000, 3, 0), [3334, 3333, 3333]),
        ((12550, 4, 10), [3452, 3451, 3451, 3451]),  # 13805 หาร 4
        ((1, 2, 50), [1, 1]),                         # 1.5 ปัดขึ้น -> 2
        ((1, 1, 0), [1]),
        ((0, 3, 100), [0, 0, 0]),
        ((999, 2, 5), [525, 524]),                    # 1048.95 -> 1049
        ((5, 2, 10), [3, 3]),                         # 5.5 -> 6
        ((10000, 3, 15), [3834, 3833, 3833]),         # 11500 หาร 3
        ((100, 3, 1), [34, 34, 33]),                  # 101 หาร 3
        ((10000.0, 2, 0), [5000, 5000]),              # float ที่เป็นจำนวนเต็มรับได้
    ]
    for args, expected in cases:
        got = split_bill(*args)
        assert got == expected, f"split_bill{args} = {got}, expected {expected}"
        due = _round_half_up(Fraction(args[0]) * (100 + args[2]) / 100)
        assert sum(got) == due, f"split_bill{args} ผลรวม {sum(got)} ไม่เท่ากับ {due}"
    print("ผ่านทุกเคส", len(cases), "เคส")
    print(split_bill(10000, 3, 0))
