import math
from fractions import Fraction

HANDLING_FEE_RATE = Fraction(125, 1000)  # 12.5%
NO_REFUND_ABOVE_PERCENT = 80


def to_frac(x):
    """รับได้ทั้ง int และ float โดยไม่เกิดคลาดเคลื่อนจาก float"""
    return Fraction(str(x))


def round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม ใช้ครั้งเดียวตอนคืนค่า"""
    return math.floor(f + Fraction(1, 2))


def refund(paid, used_percent, restock):
    """คำนวณเงินที่คืนลูกค้าของคอร์สสอนชงกาแฟ (หน่วยเป็นสตางค์)

    paid         : เงินที่ลูกค้าจ่าย (สตางค์, >= 0)
    used_percent : เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock      : True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    คืนค่าเป็นจำนวนเต็มสตางค์
    """
    if isinstance(paid, bool) or isinstance(used_percent, bool):
        raise ValueError("paid และ used_percent ต้องเป็นตัวเลข")

    paid_f = to_frac(paid)
    used_f = to_frac(used_percent)

    if paid_f < 0:
        raise ValueError("paid ต้องไม่ติดลบ")
    if used_f.denominator != 1 or not (0 <= used_f <= 100):
        raise ValueError("used_percent ต้องเป็นจำนวนเต็มระหว่าง 0-100")

    used = int(used_f)

    # เรียนไปเกิน 80% ไม่คืนเงิน
    if used > NO_REFUND_ABOVE_PERCENT:
        return 0

    # คืนตามสัดส่วนที่ยังไม่ได้เรียน
    amount = paid_f * Fraction(100 - used, 100)

    # หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    if restock:
        amount -= amount * HANDLING_FEE_RATE

    return round_half_up(amount)


if __name__ == "__main__":
    print(refund(10000, 0, False))   # 10000
    print(refund(10000, 0, True))    # 8750
    print(refund(10000, 80, False))  # 2000
    print(refund(10000, 81, False))  # 0
    print(refund(10001, 33, True))   # ทดสอบการปัดครึ่ง
