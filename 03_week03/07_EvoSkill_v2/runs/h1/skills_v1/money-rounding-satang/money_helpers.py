"""ตัวช่วยคำนวณเงินเป็นสตางค์ (อ่านอย่างเดียว · คัดลอกฟังก์ชันที่ต้องใช้ไปไว้ใน solve.py)

ทุกฟังก์ชันรับ input ที่ตรวจชนิดแล้ว และ raise ValueError เสมอเมื่อ input ผิด
"""
from fractions import Fraction
from math import floor


def need_int(value, name, low=None, high=None):
    # bool และ float ไม่ใช่ int ตามเงื่อนไขนี้
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def need_str(value, name, allowed=None):
    if type(value) is not str:
        raise ValueError(f"{name} ต้องเป็นข้อความ")
    if allowed is not None and value not in allowed:
        raise ValueError(f"{name} ไม่ถูกต้อง")
    return value


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ)"""
    return floor(Fraction(x) + Fraction(1, 2))


def round_down(x):
    """ปัดลงเป็นจำนวนเต็ม (x ไม่ติดลบ)"""
    return floor(Fraction(x))


def split_even(amount, n):
    """หารเท่ากัน คนลำดับต้นได้เพิ่มคนละ 1 สตางค์ ผลรวมเท่ากับ amount เสมอ"""
    base, extra = divmod(amount, n)
    return [base + 1] * extra + [base] * (n - extra)


if __name__ == "__main__":
    assert half_up(Fraction(12, 5)) == 2
    assert half_up(Fraction(5, 2)) == 3
    assert round_down(Fraction(199, 2)) == 99
    assert split_even(10000, 3) == [3334, 3333, 3333]
    assert sum(split_even(12345, 5)) == 12345
    for bad in (True, 1.0, "1"):
        try:
            need_int(bad, "x")
        except ValueError:
            pass
        else:
            raise AssertionError("need_int ต้อง reject ชนิดผิด")
    print("helpers ok")
