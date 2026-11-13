import math
from fractions import Fraction


def _to_int(x, name):
    """รับเฉพาะตัวเลขจำนวนเต็ม (หรือ float ที่เป็นจำนวนเต็มลงตัว) ไม่รับ bool"""
    if isinstance(x, bool):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    if isinstance(x, int):
        return x
    if isinstance(x, float) and x.is_integer():
        return int(x)
    raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม ใช้ครั้งเดียวตอนคำนวณยอดรวม"""
    return math.floor(f + Fraction(1, 2))


def split_bill(total, people, tip_percent):
    """หารบิลให้คนเท่า ๆ กัน โดยรวมทิปก่อนหาร

    total       ยอดบิล (สตางค์, >= 0)
    people      จำนวนคน (>= 1)
    tip_percent ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0-100)

    คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน
    คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์เมื่อหารไม่ลงตัว
    """
    total = _to_int(total, "total")
    people = _to_int(people, "people")
    tip_percent = _to_int(tip_percent, "tip_percent")

    if total < 0:
        raise ValueError("total ต้องไม่ติดลบ")
    if people < 1:
        raise ValueError("people ต้องอย่างน้อย 1 คน")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent ต้องอยู่ในช่วง 0-100")

    # ยอดที่ต้องหาร = ยอดบิล + ทิป (คิดเป็นเศษส่วนก่อน แล้วปัดครั้งเดียว)
    amount = _round_half_up(Fraction(total) * (100 + tip_percent) / 100)

    base, remainder = divmod(amount, people)
    return [base + 1] * remainder + [base] * (people - remainder)


if __name__ == "__main__":
    print(split_bill(10000, 3, 0))    # [3334, 3333, 3333]
    print(split_bill(10000, 4, 10))   # [2750, 2750, 2750, 2750]
    print(split_bill(12345, 3, 15))   # ทดสอบ half-up และการกระจายเศษ
