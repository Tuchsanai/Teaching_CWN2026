from fractions import Fraction


class InputError(ValueError, TypeError):
    """input ผิด — เป็นทั้ง ValueError และ TypeError"""


def _check_int(name, v, lo=None, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise InputError(f"{name} must be an int, got {v!r}")
    if lo is not None and v < lo:
        raise InputError(f"{name} must be >= {lo}")
    if hi is not None and v > hi:
        raise InputError(f"{name} must be <= {hi}")
    return v


def split_bill(total, people, tip_percent):
    _check_int("total", total, 0)
    _check_int("people", people, 1)
    _check_int("tip_percent", tip_percent, 0, 100)
    # ทิป = total*tip/100 ปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียว (ข้อสมมติ)
    tip = (2 * total * tip_percent + 100) // 200
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
