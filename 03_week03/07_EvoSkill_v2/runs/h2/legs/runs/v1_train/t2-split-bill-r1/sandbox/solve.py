import math
from fractions import Fraction


def _to_int(x, name):
    """รับค่าเป็นจำนวนเต็ม (หรือทศนิยมที่เป็นจำนวนเต็มลงตัว เช่น 10000.0) ไม่รับ bool"""
    if isinstance(x, bool):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    if isinstance(x, int):
        return x
    if isinstance(x, float) and x.is_integer():
        return int(x)
    raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม ใช้ครั้งเดียวตอนได้ยอดรวมที่ต้องหาร (ยอดไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def split_bill(total, people, tip_percent):
    """หารบิลให้ลูกค้า

    total       ยอดบิล (สตางค์, >= 0)
    people      จำนวนคน (>= 1)
    tip_percent ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)

    คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน
    """
    total = _to_int(total, "total")
    people = _to_int(people, "people")
    tip_percent = _to_int(tip_percent, "tip_percent")

    if total < 0:
        raise ValueError("total ต้องไม่ติดลบ")
    if people < 1:
        raise ValueError("people ต้องอย่างน้อย 1 คน")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent ต้องอยู่ในช่วง 0–100")

    # ยอดที่ต้องหาร = ยอดบิล + ทิป (คำนวณเป็นเศษส่วนเพื่อไม่คลาดเคลื่อน)
    amount = Fraction(total) + Fraction(total * tip_percent, 100)
    # ปัดครั้งเดียวที่ยอดรวมสตางค์
    grand = _round_half_up(amount)

    # หารเท่ากัน เศษสตางค์ให้คนลำดับแรก ๆ คนละ 1 สตางค์
    base, remainder = divmod(grand, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))   # 11000 สตางค์ / 3 = [3667, 3667, 3666]
    print(split_bill(999, 2, 0))      # [500, 499]
    print(split_bill(0, 4, 50))       # [0, 0, 0, 0]
