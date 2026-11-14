from fractions import Fraction


def refund(paid, used_percent, restock):
    # H3: ชนิดผิด -> TypeError, ช่วงผิด -> ValueError, restock ต้องเป็น bool
    if isinstance(paid, bool) or not isinstance(paid, int):
        raise TypeError("paid must be int")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int):
        raise TypeError("used_percent must be int")
    if not isinstance(restock, bool):
        raise TypeError("restock must be bool")
    if paid < 0:
        raise ValueError("paid must be >= 0")
    if not 0 <= used_percent <= 100:
        raise ValueError("used_percent must be 0-100")

    # เรียนเกิน 80% ไม่คืนเงิน
    if used_percent > 80:
        return 0

    amount = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amount *= Fraction(7, 8)  # หักค่าดำเนินการ 12.5%
    # ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
    return (2 * amount.numerator + amount.denominator) // (2 * amount.denominator)
