from fractions import Fraction

# ค่าดำเนินการเมื่อ restock = True (12.5%)
RESTOCK_FEE = Fraction(1, 8)
# เรียนไปแล้วเกินกว่านี้ (เปอร์เซ็นต์) จะไม่คืนเงิน
NO_REFUND_ABOVE = 80


def refund(paid: int, used_percent: int, restock: bool) -> int:
    """คำนวณเงินที่คืนให้ลูกค้าของคอร์สสอนชงกาแฟ (หน่วยเป็นสตางค์, จำนวนเต็ม)

    paid          เงินที่ลูกค้าจ่ายมา (สตางค์, >= 0)
    used_percent  เรียนไปแล้วกี่เปอร์เซ็นต์ (จำนวนเต็ม 0-100)
    restock       True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    if isinstance(paid, bool) or not isinstance(paid, int) or paid < 0:
        raise ValueError("paid ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int) \
            or not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็มตั้งแต่ 0 ถึง 100")

    # เรียนไปแล้วเกิน 80% ไม่คืนเงิน
    if used_percent > NO_REFUND_ABOVE:
        return 0

    # คืนตามสัดส่วนที่ยังไม่ได้เรียน (ใช้ Fraction เพื่อไม่ให้มีข้อผิดพลาดทศนิยม)
    amount = Fraction(paid * (100 - used_percent), 100)

    if restock:
        amount *= (1 - RESTOCK_FEE)  # หัก 12.5%

    # ปัดเศษแบบครึ่งขึ้นให้เป็นจำนวนเต็มสตางค์
    return int(amount + Fraction(1, 2))


if __name__ == "__main__":
    # ตัวอย่างการทดสอบอย่างง่าย
    assert refund(100000, 0, False) == 100000
    assert refund(100000, 0, True) == 87500       # หัก 12.5%
    assert refund(100000, 50, False) == 50000
    assert refund(100000, 50, True) == 43750
    assert refund(100000, 80, False) == 20000     # เท่ากับ 80% ยังคืนได้
    assert refund(100000, 81, False) == 0         # เกิน 80% ไม่คืน
    assert refund(100000, 100, True) == 0
    assert refund(0, 10, True) == 0
    assert refund(999, 33, True) == round(999 * 67 * 7 / 800)  # 586
    print("ผ่านการทดสอบทั้งหมด")
