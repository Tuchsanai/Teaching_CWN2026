from fractions import Fraction

# ข้อสมมติ: เกณฑ์ 100 บาท ใช้กับ amount ดิบ (10000 สตางค์, "ต่ำกว่า" = <)
# คูณ 2 ตอนเดือนเกิดก่อน แล้ว cap 20000 สตางค์ แล้วปัดครึ่งขึ้นครั้งเดียวท้ายสุด

class InputError(ValueError, TypeError):
    pass

_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
_MIN = 10000
_CAP = 20000


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise InputError(f"amount must be an int, got {amount!r}")
    if amount < 0:
        raise InputError("amount must be >= 0")
    if not isinstance(tier, str) or tier not in _RATES:
        raise InputError(f"unknown tier {tier!r}")
    if not isinstance(birthday, bool):
        raise InputError(f"birthday must be a bool, got {birthday!r}")
    if amount < _MIN:
        return 0
    v = amount * _RATES[tier]
    if birthday:
        v *= 2
    v = min(v, _CAP)
    return int((2 * v.numerator + v.denominator) // (2 * v.denominator))
