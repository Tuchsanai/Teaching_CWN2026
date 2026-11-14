"""BaanKafe bill splitter.

split_bill(total, people, tip_percent) -> list[int]

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม)
  1. tip      = total × tip_percent / 100   ปัดครึ่งขึ้นที่ขั้นสุดท้ายนี้เท่านั้น
  2. amount   = total + tip                 ยอดที่ต้องหาร
  3. ส่วนแบ่ง  = divmod(amount, people)       คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์
"""

from fractions import Fraction
import math


def _round_half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ใช้กับค่าไม่ติดลบ)."""
    return math.floor(Fraction(x) + Fraction(1, 2))


def split_bill(total, people, tip_percent):
    if isinstance(total, bool) or not isinstance(total, int) or total < 0:
        raise ValueError("total ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if isinstance(people, bool) or not isinstance(people, int) or people < 1:
        raise ValueError("people ต้องเป็นจำนวนเต็มตั้งแต่ 1")
    if isinstance(tip_percent, bool) or not isinstance(tip_percent, int) \
            or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent ต้องเป็นจำนวนเต็ม 0–100")

    # ขั้น 1: ทิปคิดจากยอดบิล ปัดครั้งเดียวที่ขั้นนี้
    tip = _round_half_up(Fraction(total * tip_percent, 100))
    # ขั้น 2: ยอดที่ต้องหาร = ยอดบิล + ทิป
    amount = total + tip
    # ขั้น 3: หารเท่ากัน เศษสตางค์ให้คนลำดับแรก ๆ คนละ 1 สตางค์
    q, r = divmod(amount, people)
    shares = [q + 1 if i < r else q for i in range(people)]

    assert sum(shares) == amount
    return shares


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # 11000 / 3 -> [3667, 3667, 3666]
