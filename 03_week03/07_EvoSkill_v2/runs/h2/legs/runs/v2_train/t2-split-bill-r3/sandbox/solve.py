import math
from fractions import Fraction


def _to_frac(x, name):
    """แปลงค่าตัวเลขเป็น Fraction โดยไม่ผ่าน float แบบคลาดเคลื่อน"""
    if isinstance(x, bool) or not isinstance(x, (int, float, Fraction)):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    return Fraction(str(x)) if isinstance(x, float) else Fraction(x)


def split_bill(total, people, tip_percent):
    """หารบิลของ BaanKafe

    total       ยอดบิล (สตางค์, >= 0)
    people      จำนวนคน (>= 1)
    tip_percent ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0-100)

    คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน
    """
    t = _to_frac(total, "total")
    p = _to_frac(people, "people")
    tip = _to_frac(tip_percent, "tip_percent")

    if t < 0:
        raise ValueError("total ต้องไม่ติดลบ")
    if p < 1 or p.denominator != 1:
        raise ValueError("people ต้องเป็นจำนวนเต็มตั้งแต่ 1")
    if tip < 0 or tip > 100 or tip.denominator != 1:
        raise ValueError("tip_percent ต้องเป็นจำนวนเต็ม 0-100")

    # ยอดที่ต้องหาร = ยอดบิล + ทิป (คิดเป็นเศษส่วนก่อน)
    amount = t + t * tip / 100
    # ปัดครึ่งขึ้นครั้งเดียวที่ยอดรวม (ไม่ใช้ round() เพราะปัดเลขคู่)
    grand = math.floor(amount + Fraction(1, 2))

    n = int(p)
    base, remainder = divmod(grand, n)
    # คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบเศษ
    return [base + 1 if i < remainder else base for i in range(n)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # [3667, 3667, 3666]
