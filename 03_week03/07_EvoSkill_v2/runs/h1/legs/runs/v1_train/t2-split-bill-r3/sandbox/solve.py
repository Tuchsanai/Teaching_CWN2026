"""BaanKafe: split_bill(total, people, tip_percent) สำหรับหารบิล

กติกา (ตามโจทย์):
- total        = ยอดบิลเป็นสตางค์ จำนวนเต็ม >= 0
- people       = จำนวนคน จำนวนเต็ม >= 1
- tip_percent  = ทิปเป็นเปอร์เซ็นต์ จำนวนเต็ม 0..100
- ยอดที่ต้องหาร = ยอดบิล + ทิป
- หารเท่ากันทุกคน ถ้าหารไม่ลงตัว คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ
- คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน

การตัดสินใจเองที่โจทย์ไม่ได้ระบุ:
- ยอดที่ต้องหาร = total * (100 + tip_percent) / 100 คำนวณใน Fraction แล้วปัดครึ่งขึ้น
  เป็นสตางค์ "ครั้งเดียว" ตอนท้าย (ไม่ปัดทิปแยกก่อนบวก) เพราะยอดที่ลูกค้าต้องจ่ายเป็นของร้าน
"""

import json
import sys
from fractions import Fraction
from math import floor


def _need_int(value, name, low=None, high=None):
    # bool และ float ไม่ถือเป็น int ในที่นี้ (type() ตรง ๆ ไม่ใช่ isinstance)
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.4 -> 2, 2.5 -> 3"""
    return floor(Fraction(x) + Fraction(1, 2))


def split_even(amount, n):
    """หารเท่ากัน คนลำดับต้นได้เพิ่มคนละ 1 สตางค์ ผลรวมเท่ากับ amount เสมอ"""
    base, extra = divmod(amount, n)
    return [base + 1] * extra + [base] * (n - extra)


def split_bill(total, people, tip_percent):
    total = _need_int(total, "total", low=0)
    people = _need_int(people, "people", low=1)
    tip_percent = _need_int(tip_percent, "tip_percent", low=0, high=100)

    amount = half_up(Fraction(total) * (100 + tip_percent) / 100)
    return split_even(amount, people)


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
