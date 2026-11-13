"""refund() ของ BaanKafe — โหมดปัดเศษ r2: ครึ่งไปหาเลขคู่ (banker's) ครั้งเดียวที่ค่าสุดท้าย
ข้อสมมติ: ใช้ Fraction ล้วน; used_percent > 80 -> 0; restock หัก 12.5% ของยอดที่จะคืน (คูณ 7/8)
"""
from fractions import Fraction


class InputError(ValueError, TypeError):
    """input ผิด — เป็นทั้ง ValueError และ TypeError"""


def _check_int(name, v, lo, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise InputError(f"{name} must be an int, got {v!r}")
    if v < lo or (hi is not None and v > hi):
        raise InputError(f"{name} out of range: {v!r}")


def refund(paid, used_percent, restock):
    _check_int("paid", paid, 0)
    _check_int("used_percent", used_percent, 0, 100)
    if not isinstance(restock, bool):
        raise InputError(f"restock must be a bool, got {restock!r}")
    if used_percent > 80:
        return 0
    amount = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amount *= Fraction(875, 1000)
    return int(round(amount))
