"""BaanKafe: คำนวณเงินคืนของคอร์สสอนชงกาแฟ

กติกา
- paid: เงินที่ลูกค้าจ่าย (สตางค์ จำนวนเต็ม >= 0)
- used_percent: เรียนไปแล้วกี่เปอร์เซ็นต์ (จำนวนเต็ม 0-100)
- restock: True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
- คืนตามสัดส่วนที่ยังไม่ได้เรียน
- เรียนไปแล้วเกิน 80% ไม่คืนเงิน
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดเศษแบบปัดครึ่งขึ้น)
"""

from fractions import Fraction

MAX_USED_FOR_REFUND = 80          # เกินนี้ไม่คืนเงิน
RESTOCK_FEE = Fraction(125, 1000)  # 12.5%


def refund(paid: int, used_percent: int, restock: bool) -> int:
    """คืนจำนวนเงิน (สตางค์, จำนวนเต็ม) ที่ต้องคืนให้ลูกค้า"""
    if isinstance(paid, bool) or not isinstance(paid, int) or paid < 0:
        raise ValueError("paid ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int) \
            or not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็ม 0-100")

    if used_percent > MAX_USED_FOR_REFUND:
        return 0

    # ยอดตามสัดส่วนที่ยังไม่ได้เรียน (คิดแบบเศษส่วนเพื่อไม่คลาดเคลื่อน)
    amount = Fraction(paid * (100 - used_percent), 100)

    if restock:
        amount -= amount * RESTOCK_FEE

    # ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์
    return int(amount + Fraction(1, 2))


if __name__ == "__main__":
    print(refund(10000, 20, False))  # 8000
    print(refund(10000, 20, True))   # 7000
    print(refund(1001, 0, True))     # 876
    print(refund(10000, 81, False))  # 0
