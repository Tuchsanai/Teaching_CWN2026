from fractions import Fraction

# สมมติฐาน: เกณฑ์ 100 บาท ใช้กับยอดดิบ; คูณ 2 ก่อน แล้วค่อย cap 200 บาท; ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
_RATES = {"silver": Fraction(3, 200), "gold": Fraction(1, 40), "platinum": Fraction(1, 25)}
_MIN = 10000   # 100 บาท
_CAP = 20000   # 200 บาท


class InputError(ValueError, TypeError):
    """input ผิด — เป็นทั้ง ValueError และ TypeError"""


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise InputError(f"amount must be an int, got {amount!r}")
    if amount < 0:
        raise InputError("amount must be >= 0")
    if not isinstance(tier, str) or tier not in _RATES:
        raise InputError(f"unknown tier: {tier!r}")
    if not isinstance(birthday, bool):
        raise InputError(f"birthday must be a bool, got {birthday!r}")
    if amount < _MIN:
        return 0
    v = amount * _RATES[tier]
    if birthday:
        v *= 2
    if v > _CAP:
        return _CAP
    return int((2 * v.numerator + v.denominator) // (2 * v.denominator))
