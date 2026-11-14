"""BaanKafe: หารบิล (หน่วยสตางค์)"""
from fractions import Fraction


def _need_int(value, name, low, high=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if value < low or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def split_bill(total, people, tip_percent):
    _need_int(total, "total", 0)
    _need_int(people, "people", 1)
    _need_int(tip_percent, "tip_percent", 0, 100)
    grand = Fraction(total) * (100 + tip_percent) / 100
    grand = int((grand * 2 + 1) // 2)  # ปัดครึ่งขึ้นครั้งเดียว
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
