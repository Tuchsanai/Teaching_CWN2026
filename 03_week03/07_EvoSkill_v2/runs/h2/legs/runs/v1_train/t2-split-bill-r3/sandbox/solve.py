from fractions import Fraction
import math


def _round_half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ใช้กับค่าไม่ติดลบ)"""
    return math.floor(Fraction(x) + Fraction(1, 2))


def split_bill(total, people, tip_percent):
    """
    หารบิลของร้าน BaanKafe

    total        ยอดบิล (สตางค์, >= 0)
    people       จำนวนคน (>= 1)
    tip_percent  ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)

    ลำดับการคิด:
      1) ทิป = ยอดบิล × tip_percent / 100 ปัดครึ่งขึ้นเป็นสตางค์ (ปัดครั้งเดียวที่ขั้นนี้)
      2) ยอดที่ต้องหาร = ยอดบิล + ทิป
      3) หารเท่ากัน หารไม่ลงตัวให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์

    คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน
    """
    if total < 0:
        raise ValueError("total ต้องไม่ติดลบ")
    if people < 1:
        raise ValueError("people ต้องอย่างน้อย 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent ต้องอยู่ระหว่าง 0 ถึง 100")

    tip = _round_half_up(Fraction(total * tip_percent, 100))
    grand_total = total + tip

    q, r = divmod(grand_total, people)
    return [q + 1 if i < r else q for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # [3667, 3667, 3666]
