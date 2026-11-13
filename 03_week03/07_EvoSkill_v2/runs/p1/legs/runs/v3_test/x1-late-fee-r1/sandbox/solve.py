"""late_fee — โหมดปัดเศษ r1: ปัดครึ่งขึ้น (round half up) ครั้งเดียวที่ค่าปรับสุดท้าย

ข้อสมมติ:
- days_late <= 3 -> 0; มิฉะนั้นอัตรา = days_late * 0.75% (นับรวม 3 วันแรก)
- cap 15% ของยอดค้าง เทียบแบบ Fraction ก่อนปัด แล้วปัดครั้งเดียว
"""
from fractions import Fraction


class InputError(ValueError, TypeError):
    """input ผิด — เป็นทั้ง ValueError และ TypeError"""


def _check_int(name, v, lo, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise InputError(f"{name} must be an int, got {v!r}")
    if v < lo:
        raise InputError(f"{name} must be >= {lo}")
    if hi is not None and v > hi:
        raise InputError(f"{name} must be <= {hi}")
    return v


def _round_half_up(x):
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def late_fee(amount, days_late):
    _check_int("amount", amount, 0)
    _check_int("days_late", days_late, 0, 365)
    if days_late <= 3:
        return 0
    fee = Fraction(amount * days_late * 3, 400)  # 0.75% = 3/400 ต่อวัน
    cap = Fraction(amount * 3, 20)               # 15%
    return int(_round_half_up(min(fee, cap)))
