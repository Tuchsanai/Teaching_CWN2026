from fractions import Fraction


def refund(paid: int, used_percent: int, restock: bool) -> int:
    """คำนวณยอดเงินคืนของคอร์สสอนชงกาแฟ BaanKafe (หน่วยเป็นสตางค์ จำนวนเต็ม)

    paid         เงินที่ลูกค้าจ่ายมา (สตางค์, >= 0)
    used_percent เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock      True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน

    กติกา:
      - เรียนไปแล้วเกิน 80% ไม่คืนเงิน (คืน 0)
      - คืนตามสัดส่วนที่ยังไม่ได้เรียน = paid * (100 - used_percent) / 100
      - ถ้า restock เป็น True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
      - ผลลัพธ์ปัดเศษลง (floor) ให้เป็นจำนวนเต็มสตางค์
    """
    if isinstance(paid, bool) or not isinstance(paid, int):
        raise TypeError("paid ต้องเป็นจำนวนเต็ม (สตางค์)")
    if paid < 0:
        raise ValueError("paid ต้องไม่ติดลบ")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int):
        raise TypeError("used_percent ต้องเป็นจำนวนเต็ม")
    if not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องอยู่ระหว่าง 0 ถึง 100")

    if used_percent > 80:
        return 0

    # ใช้เศษส่วนเพื่อหลีกเลี่ยงความคลาดเคลื่อนของทศนิยม (floating point)
    amount = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amount -= amount * Fraction(125, 1000)  # หัก 12.5%

    return amount.numerator // amount.denominator  # floor -> จำนวนเต็มสตางค์


if __name__ == "__main__":
    assert refund(10000, 0, False) == 10000
    assert refund(10000, 0, True) == 8750
    assert refund(10000, 50, False) == 5000
    assert refund(10000, 50, True) == 4375
    assert refund(10000, 80, False) == 2000
    assert refund(10000, 81, False) == 0
    assert refund(10000, 100, True) == 0
    assert refund(0, 10, True) == 0
    assert refund(999, 33, True) == 585  # 999*67/100 = 669.33 -> *7/8 = 585.66 -> 585
    print("all tests passed")
