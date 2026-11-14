"""BaanKafe bill splitter.

หน่วยทั้งหมดเป็นจำนวนเต็มสตางค์ ไม่ใช้ float
- ทิป = ปัดครึ่งขึ้นครั้งเดียวที่ขั้นสุดท้ายของการคำนวณทิป (ค่าเริ่มต้นตามสกิล satang-money-math)
- ยอดที่ต้องหาร = ยอดบิล + ทิป
- หารเท่ากันทุกคน เศษสตางค์ให้คนลำดับแรก ๆ คนละ 1 สตางค์
"""

import math
from fractions import Fraction


def split_bill(total, people, tip_percent):
    """หารบิลให้ลูกค้า แล้วคืน list ของยอดที่แต่ละคนจ่าย (สตางค์, int) เรียงตามลำดับคน"""
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise ValueError("total ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if not isinstance(people, int) or isinstance(people, bool) or people < 1:
        raise ValueError("people ต้องเป็นจำนวนเต็มตั้งแต่ 1")
    if not isinstance(tip_percent, int) or isinstance(tip_percent, bool) or not (0 <= tip_percent <= 100):
        raise ValueError("tip_percent ต้องเป็นจำนวนเต็มระหว่าง 0 ถึง 100")

    # 1) ทิปคิดเป็นเศษส่วนก่อน แล้วปัดครึ่งขึ้นครั้งเดียวที่ขั้นสุดท้าย
    tip_exact = Fraction(total * tip_percent, 100)
    tip = math.floor(tip_exact + Fraction(1, 2))

    # 2) ยอดที่ต้องหาร = ยอดบิล + ทิป (จำนวนเต็มสตางค์)
    amount = total + tip

    # 3) หารเท่ากัน เศษให้คนลำดับแรก ๆ คนละ 1 สตางค์
    q, r = divmod(amount, people)
    shares = [q + 1 if i < r else q for i in range(people)]

    assert sum(shares) == amount
    return shares


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # 10,000 + ทิป 1,000 = 11,000 -> [3667, 3667, 3666]
