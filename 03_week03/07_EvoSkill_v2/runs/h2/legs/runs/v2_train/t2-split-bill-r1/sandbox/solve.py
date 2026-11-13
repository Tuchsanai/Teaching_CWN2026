from fractions import Fraction
import math


def _to_int(value, name):
    """รับจำนวนเต็ม หรือ float ที่เป็นจำนวนเต็มพอดี (เช่น 10000.0) ไม่รับ bool"""
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a number, not bool")
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    raise ValueError(f"{name} must be an integer")


def split_bill(total, people, tip_percent):
    """หารบิลของ BaanKafe

    total        ยอดบิลเป็นสตางค์ (>= 0)
    people       จำนวนคน (>= 1)
    tip_percent  ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0-100)

    คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน
    """
    total = _to_int(total, "total")
    people = _to_int(people, "people")
    tip_percent = _to_int(tip_percent, "tip_percent")

    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be between 0 and 100")

    # ยอดบิลบวกทิปเป็นเศษส่วนก่อน แล้วปัดครึ่งขึ้นครั้งเดียว
    amount = Fraction(total) * (100 + tip_percent) / 100
    grand_total = math.floor(amount + Fraction(1, 2))

    # หารให้เท่ากัน เศษ (สตางค์) ให้คนลำดับแรก ๆ คนละ 1 สตางค์
    base, remainder = divmod(grand_total, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # [3667, 3667, 3666]
