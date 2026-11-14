"""BaanKafe: หารบิลระหว่างคน

กติกา
- total        = ยอดบิล หน่วยสตางค์ int >= 0
- people       = จำนวนคน int >= 1
- tip_percent  = ทิปเป็นเปอร์เซ็นต์ int 0..100
- ยอดที่ต้องหาร = total + ทิป (total * tip_percent / 100) คำนวณใน Fraction
  แล้วปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ "ครั้งเดียว" ตอนท้าย
- หารเท่ากันทุกคน ถ้าไม่ลงตัว คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์
- คืน list ของยอดที่แต่ละคนจ่าย (int สตางค์) เรียงตามลำดับคน
"""

import json
import sys
from fractions import Fraction
from math import floor


def _half_up(x):
    # ปัดครึ่งขึ้น สำหรับ x >= 0: 2.4 -> 2, 2.5 -> 3
    return floor(Fraction(x) + Fraction(1, 2))


def _check_int(name, value):
    # ห้าม bool, float และ string แม้ค่าจะดูเหมือนจำนวนเต็ม
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม (int)")
    return value


def split_bill(total, people, tip_percent):
    total = _check_int("total", total)
    people = _check_int("people", people)
    tip_percent = _check_int("tip_percent", tip_percent)

    if total < 0:
        raise ValueError("total ต้องไม่ต่ำกว่า 0")
    if people < 1:
        raise ValueError("people ต้องตั้งแต่ 1 ขึ้นไป")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent ต้องอยู่ระหว่าง 0 ถึง 100")

    # ยอดที่ต้องหาร = total + total * tip% ปัดครั้งเดียวตอนท้าย
    amount = _half_up(Fraction(total) * (100 + tip_percent) / 100)

    base, extra = divmod(amount, people)
    return [base + 1] * extra + [base] * (people - extra)


def main():
    try:
        raw = sys.stdin.read()
        args = json.loads(raw)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = split_bill(**args)
    except (ValueError, TypeError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
