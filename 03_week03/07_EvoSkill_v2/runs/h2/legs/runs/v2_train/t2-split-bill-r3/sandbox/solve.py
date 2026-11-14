"""BaanKafe: หารบิล

ลำดับการคิด:
1. ทิป = floor(total × tip_percent / 100)   (ปัดลงที่ขั้นสุดท้าย เพราะโจทย์ไม่ได้ระบุการปัดทิป)
2. ยอดที่ต้องหาร = total + ทิป
3. หารเท่ากันทุกคน: คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ เศษที่เหลือจึงกระจายจากหน้า

ทุกค่าเป็นจำนวนเต็มสตางค์ ไม่ใช้ float
"""

from fractions import Fraction
import math


def split_bill(total, people, tip_percent):
    """คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน

    total: ยอดบิลเป็นสตางค์ (>= 0)
    people: จำนวนคน (>= 1)
    tip_percent: ทิปเป็นเปอร์เซ็นต์ จำนวนเต็ม 0–100
    """
    if isinstance(total, bool) or not isinstance(total, int) or total < 0:
        raise ValueError("total ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if isinstance(people, bool) or not isinstance(people, int) or people < 1:
        raise ValueError("people ต้องเป็นจำนวนเต็มตั้งแต่ 1")
    if isinstance(tip_percent, bool) or not isinstance(tip_percent, int) or not (0 <= tip_percent <= 100):
        raise ValueError("tip_percent ต้องเป็นจำนวนเต็มระหว่าง 0 ถึง 100")

    # 1) ทิปปัดลงที่ขั้นสุดท้าย
    tip = math.floor(Fraction(total * tip_percent, 100))

    # 2) ยอดที่ต้องหาร
    amount = total + tip

    # 3) หารลงตัวหรือเศษกระจายให้คนแรก ๆ คนละ 1 สตางค์
    q, r = divmod(amount, people)
    return [q + 1 if i < r else q for i in range(people)]


if __name__ == "__main__":
    # ตัวอย่าง: บิล 1000 สตางค์ 3 คน ทิป 10% -> ทิป 100, ยอด 1100, หาร 3 ได้ 367, 367, 366
    print(split_bill(1000, 3, 10))
