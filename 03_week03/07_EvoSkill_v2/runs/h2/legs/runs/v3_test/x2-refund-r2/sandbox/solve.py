from fractions import Fraction


def round_half_even(x):
    """ปัดครึ่งเข้าเลขคู่ (ค่าเริ่มต้นของการปัดเงินลูกค้า)"""
    return round(Fraction(x))


def refund(paid, used_percent, restock):
    """คำนวณเงินคืนค่าคอร์สสอนชงกาแฟ (หน่วยเป็นสตางค์ ปัดเป็นจำนวนเต็ม)

    paid          : เงินที่ลูกค้าจ่าย (สตางค์, >= 0)
    used_percent  : เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock       : True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    if paid < 0:
        raise ValueError("paid ต้องไม่ติดลบ")
    if not (0 <= used_percent <= 100):
        raise ValueError("used_percent ต้องอยู่ระหว่าง 0-100")

    # เรียนไปแล้วเกิน 80% ไม่คืนเงิน (พอดี 80% ยังคืนได้)
    if used_percent > 80:
        return 0

    # 1) คืนตามสัดส่วนที่ยังไม่ได้เรียน (คิดเป็นเศษส่วนทั้งหมด ยังไม่ปัด)
    amount = Fraction(paid) * Fraction(100 - used_percent, 100)

    # 2) หักค่าดำเนินการ 12.5% ของยอดที่จะคืน = เหลือ 87.5% (7/8)
    if restock:
        amount = amount * Fraction(7, 8)

    # 3) ปัดครั้งเดียวที่ขั้นสุดท้าย (round-half-even) ได้จำนวนเต็มสตางค์
    return int(round_half_even(amount))


if __name__ == "__main__":
    print(refund(10000, 0, False))   # 10000
    print(refund(10000, 30, False))  # 7000
    print(refund(10000, 30, True))   # 6125
    print(refund(10000, 80, False))  # 2000
    print(refund(10000, 81, False))  # 0
