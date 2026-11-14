from fractions import Fraction


def refund(paid, used_percent, restock):
    # H2: any invalid input -> ValueError
    if isinstance(paid, bool) or not isinstance(paid, int) or paid < 0:
        raise ValueError("paid")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int) or not 0 <= used_percent <= 100:
        raise ValueError("used_percent")
    if not isinstance(restock, bool):
        raise ValueError("restock")
    if used_percent > 80:
        return 0
    amt = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amt *= Fraction(7, 8)  # หัก 12.5%
    # ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
    return (2 * amt.numerator + amt.denominator) // (2 * amt.denominator)
