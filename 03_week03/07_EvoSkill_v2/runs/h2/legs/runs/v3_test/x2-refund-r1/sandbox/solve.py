from fractions import Fraction

RESTOCK_FEE_RATE = Fraction(125, 1000)  # ค่าดำเนินการ 12.5% ของยอดที่จะคืน
NO_REFUND_ABOVE_PERCENT = 80            # เรียนไปแล้วเกิน 80% ไม่คืนเงิน


def refund(paid, used_percent, restock):
    """คำนวณเงินที่ต้องคืนลูกค้า (หน่วยสตางค์, จำนวนเต็ม)

    paid         : เงินที่ลูกค้าจ่าย (สตางค์, >= 0)
    used_percent : เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock      : True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน

    ลำดับการคิด:
      1. ถ้าเรียนไปแล้วเกิน 80% -> คืน 0
      2. ยอดคืนตามสัดส่วนที่ยังไม่ได้เรียน = paid * (100 - used_percent) / 100
      3. ถ้า restock = True -> หักค่าดำเนินการ 12.5% ของยอดข้อ 2
      4. ปัดเศษครั้งเดียวที่ขั้นสุดท้าย (round-half-even, ค่าเริ่มต้นของสกิล)
    """
    if paid < 0:
        raise ValueError("paid must be >= 0 (satang)")
    if not 0 <= used_percent <= 100:
        raise ValueError("used_percent must be an integer between 0 and 100")

    if used_percent > NO_REFUND_ABOVE_PERCENT:
        return 0

    amount = Fraction(paid) * Fraction(100 - used_percent, 100)
    if restock:
        amount -= amount * RESTOCK_FEE_RATE

    return round(amount)
