"""ตัวอย่างเครื่องมือ (อ่านอย่างเดียว) — คัดลอกไปใช้ใน solve.py ได้
"""
from fractions import Fraction


def round_half_up(x):
    """ปัดครึ่งขึ้นสำหรับค่าไม่ติดลบ (รับ int/Fraction) คืน int"""
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def check_int(name, v, lo=None, hi=None):
    """ตรวจจำนวนเต็ม (ไม่รับ bool) และช่วงค่า ไม่ผ่านให้ ValueError"""
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be an int, got {v!r}")
    if lo is not None and v < lo:
        raise ValueError(f"{name} must be >= {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} must be <= {hi}")
    return v
