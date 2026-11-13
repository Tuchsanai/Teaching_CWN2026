"""BaanKafe bill splitter.

split_bill(total, people, tip_percent) -> list[int]
  total        ยอดบิล หน่วยสตางค์ (int, >= 0)
  people       จำนวนคน (int, >= 1)
  tip_percent  ทิปเป็นเปอร์เซ็นต์ (int, 0..100)

คืน list ของยอดที่แต่ละคนจ่าย (int สตางค์) เรียงตามลำดับคน
"""

from fractions import Fraction


def _require_int(value, label, lo=None, hi=None):
    # ใช้ type() ไม่ใช้ isinstance() เพราะ bool เป็น subclass ของ int
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม (int)")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and value > hi:
        raise ValueError(f"{label} ต้องไม่เกิน {hi}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม รับ int หรือ Fraction ที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def split_bill(total, people, tip_percent):
    total = _require_int(total, "total", lo=0)
    people = _require_int(people, "people", lo=1)
    tip_percent = _require_int(tip_percent, "tip_percent", lo=0, hi=100)

    # ยอดที่ต้องหาร = ยอดบิล + ทิป (ทิปคิดจากยอดบิล)
    # คำนวณเป็นเศษส่วนที่แน่นอน แล้วปัดครั้งเดียวตอนท้าย
    grand_total = _half_up(Fraction(total * (100 + tip_percent), 100))

    # หารเท่ากัน ส่วนเหลือให้คนลำดับแรก ๆ คนละ 1 สตางค์
    base, extra = divmod(grand_total, people)
    return [base + 1] * extra + [base] * (people - extra)


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # 11000 -> [3667, 3667, 3666]
    print(split_bill(9000, 3, 0))    # [3000, 3000, 3000]
