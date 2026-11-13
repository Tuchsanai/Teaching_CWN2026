"""late_fee — BaanKafe. โหมดปัดเศษ: r2 (ครึ่งไปหาเลขคู่ / banker's ครั้งเดียวตอนท้าย)

ข้อสมมติ: ช้า > 3 วัน -> ค่าปรับ = amount * 0.75% * days_late (นับทุกวัน) แล้ว cap ที่ 15% ของ amount
ก่อนปัดเศษ; ช้า <= 3 วัน -> 0
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


def late_fee(amount, days_late):
    _check_int("amount", amount, 0)
    _check_int("days_late", days_late, 0, 365)
    if days_late <= 3:
        return 0
    fee = Fraction(amount * 75 * days_late, 10000)
    cap = Fraction(amount * 15, 100)
    return int(round(min(fee, cap)))
