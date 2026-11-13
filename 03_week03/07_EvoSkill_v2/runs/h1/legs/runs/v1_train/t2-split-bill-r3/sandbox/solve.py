from fractions import Fraction


def _require_int(value, label, lo=None, hi=None):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and value > hi:
        raise ValueError(f"{label} ต้องไม่เกิน {hi}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม รับ int หรือ Fraction ที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def split_bill(total, people, tip_percent):
    """หารบิลให้คนทั้งหมด คืน list ของยอดที่แต่ละคนจ่าย (สตางค์ int) เรียงตามลำดับคน

    total        ยอดบิลเป็นสตางค์ (>= 0)
    people       จำนวนคน (>= 1)
    tip_percent  ทิปเป็นเปอร์เซ็นต์ จำนวนเต็ม 0-100
    """
    _require_int(total, "total", lo=0)
    _require_int(people, "people", lo=1)
    _require_int(tip_percent, "tip_percent", lo=0, hi=100)

    # ยอดที่ต้องหาร = ยอดบิล + ทิป เก็บเป็นเศษส่วนแล้วปัดครึ่งขึ้นครั้งเดียว
    amount = _half_up(Fraction(total) * (100 + tip_percent) / 100)

    # หารเท่ากัน เศษสตางค์ให้คนลำดับแรก ๆ คนละ 1 สตางค์
    base, extra = divmod(amount, people)
    return [base + 1] * extra + [base] * (people - extra)


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))   # [3667, 3667, 3666]
    print(split_bill(1000, 3, 0))     # [334, 333, 333]
    print(split_bill(1, 2, 50))       # [1, 1]  (1.5 -> 2 -> 1+1)
    print(split_bill(5000, 4, 15))    # [1438, 1438, 1437, 1437]
