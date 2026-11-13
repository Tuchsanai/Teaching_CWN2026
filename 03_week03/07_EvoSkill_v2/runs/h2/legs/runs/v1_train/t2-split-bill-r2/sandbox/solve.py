import math
from fractions import Fraction


def _to_frac(x):
    """แปลงตัวเลขเป็น Fraction ผ่านข้อความ เพื่อไม่ให้เกิดคลาดเคลื่อนจาก float"""
    if isinstance(x, bool) or not isinstance(x, (int, float, Fraction)):
        raise ValueError(f"ค่าต้องเป็นตัวเลข: {x!r}")
    return Fraction(str(x)) if not isinstance(x, Fraction) else x


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม ใช้ครั้งเดียวตอนคืนค่า"""
    return math.floor(f + Fraction(1, 2))


def split_bill(total, people, tip_percent):
    """หารบิลให้ BaanKafe

    total        ยอดบิลเป็นสตางค์ (>= 0)
    people       จำนวนคน (>= 1)
    tip_percent  ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0-100)

    คืน list ของยอดที่แต่ละคนจ่ายเป็นจำนวนเต็มสตางค์ เรียงตามลำดับคน
    คนลำดับต้น ๆ จ่ายเพิ่มคนละ 1 สตางค์เมื่อหารไม่ลงตัว
    """
    t = _to_frac(total)
    p = _to_frac(people)
    tip = _to_frac(tip_percent)

    if t < 0:
        raise ValueError("ยอดบิลต้องไม่ติดลบ")
    if p.denominator != 1 or p < 1:
        raise ValueError("จำนวนคนต้องเป็นจำนวนเต็มตั้งแต่ 1")
    if tip.denominator != 1 or not (0 <= tip <= 100):
        raise ValueError("ทิปต้องเป็นจำนวนเต็ม 0-100")

    people_n = int(p)

    # ยอดที่ต้องหาร = ยอดบิล + ทิป (คำนวณแบบแม่นยำ แล้วปัดครั้งเดียว)
    amount = _round_half_up(t + t * tip / 100)

    base, remainder = divmod(amount, people_n)
    return [base + 1 if i < remainder else base for i in range(people_n)]


if __name__ == "__main__":
    # ตัวอย่างและการทดสอบพื้นฐาน
    assert split_bill(10000, 4, 0) == [2500, 2500, 2500, 2500]
    assert split_bill(10000, 3, 0) == [3334, 3333, 3333]
    assert split_bill(10000, 3, 10) == [3667, 3667, 3666]  # 11000 / 3
    assert split_bill(0, 2, 15) == [0, 0]
    assert split_bill(1, 3, 0) == [1, 0, 0]
    assert split_bill(333, 2, 0) == [167, 166]
    # ทิปไม่เป็นจำนวนสตางค์เต็ม: 101 * 0.05 = 5.05 -> 106.05 -> ปัดเป็น 106
    assert split_bill(101, 1, 5) == [106]
    # ทิป 50% ของ 1 สตางค์ = 0.5 -> 1.5 -> ปัดครึ่งขึ้นเป็น 2
    assert split_bill(1, 1, 50) == [2]
    assert sum(split_bill(12345, 7, 13)) == _round_half_up(Fraction(12345 * 113, 100))
    print("ทดสอบผ่านทั้งหมด")
