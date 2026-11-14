from fractions import Fraction
import math


def split_bill(total, people, tip_percent):
    """หารบิลของ BaanKafe

    total: ยอดบิล (สตางค์, ตั้งแต่ 0)
    people: จำนวนคน (ตั้งแต่ 1)
    tip_percent: ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0-100)

    คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน
    """
    if total < 0 or people < 1 or not (0 <= tip_percent <= 100):
        raise ValueError("invalid input: total>=0, people>=1, 0<=tip_percent<=100")

    # ขั้นที่ 1: ทิป = ยอดบิล × tip% ปัดลง (ตัดเศษสตางค์ทิ้ง) ที่ขั้นสุดท้ายของการคำนวณทิป
    tip = math.floor(Fraction(total) * Fraction(tip_percent, 100))

    # ขั้นที่ 2: ยอดที่ต้องหาร = ยอดบิล + ทิป
    amount = total + tip

    # ขั้นที่ 3: หารเท่ากัน เศษสตางค์ให้คนลำดับแรก ๆ คนละ 1 สตางค์
    q, r = divmod(amount, people)
    return [q + 1 if i < r else q for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # [3667, 3667, 3666]
