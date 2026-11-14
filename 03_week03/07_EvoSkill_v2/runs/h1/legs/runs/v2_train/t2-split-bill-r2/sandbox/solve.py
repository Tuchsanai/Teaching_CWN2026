"""BaanKafe: หารบิล

กติกา
- total = ยอดบิล (สตางค์, int, >= 0)
- people = จำนวนคน (int, >= 1)
- tip_percent = ทิปเป็นเปอร์เซ็นต์ (int, 0–100)
- ยอดที่ต้องหาร = total + ทิป (total * tip_percent / 100) ปัดครั้งเดียวเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น)
- หารเท่ากันทุกคน ถ้าไม่ลงตัว คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์
- คืน list ของยอดที่แต่ละคนจ่าย (int สตางค์) เรียงตามลำดับคน
"""
import json
import sys
from fractions import Fraction
from math import floor


def _need_int(value, name, low=None, high=None):
    # bool เป็น subclass ของ int จึงต้องเช็ค type ตรง ๆ
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x >= 0)"""
    return floor(Fraction(x) + Fraction(1, 2))


def _split_even(amount, n):
    """หารเท่ากัน คนลำดับต้นได้เพิ่มคนละ 1 สตางค์ ผลรวมเท่ากับ amount เสมอ"""
    base, extra = divmod(amount, n)
    return [base + 1] * extra + [base] * (n - extra)


def split_bill(total, people, tip_percent):
    total = _need_int(total, "total", low=0)
    people = _need_int(people, "people", low=1)
    tip_percent = _need_int(tip_percent, "tip_percent", low=0, high=100)

    # คำนวณทั้งสายใน Fraction แล้วปัดครั้งเดียวตอนท้าย
    payable = _half_up(Fraction(total) * (100 + tip_percent) / 100)
    return _split_even(payable, people)


def main():
    try:
        args = json.loads(sys.stdin.read())
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = split_bill(**args)
    except (ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
