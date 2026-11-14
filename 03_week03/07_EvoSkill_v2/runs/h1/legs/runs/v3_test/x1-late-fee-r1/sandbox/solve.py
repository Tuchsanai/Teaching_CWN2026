"""BaanKafe: คิดค่าปรับลูกค้าขายส่งที่ชำระเงินช้า

กติกา:
- amount = ยอดค้างชำระ เป็นสตางค์ จำนวนเต็ม >= 0
- days_late = จำนวนวันที่ช้า จำนวนเต็ม 0–365
- ช้าไม่เกิน 3 วัน (days_late <= 3) ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน (days_late > 3) คิดค่าปรับวันละ 0.75% ของยอดค้างชำระ
  นับทุกวันที่ช้า รวม 3 วันแรก
- ค่าปรับสูงสุด 15% ของยอดค้างชำระ
- ผลเป็นจำนวนเต็มสตางค์ ปัดครั้งเดียวที่ท้ายสุด ปัดครึ่งขึ้น
  (เป็นยอดที่ลูกค้าต้องจ่าย ตามสกิล money-rounding-satang)
"""

import json
import sys
from fractions import Fraction
from math import floor

GRACE_DAYS = 3
DAILY_RATE = Fraction(75, 10000)   # 0.75% ต่อวัน
CAP_RATE = Fraction(15, 100)       # เพดาน 15%
MAX_DAYS = 365


def _half_up(x):
    # ปัดครึ่งขึ้น สำหรับ x >= 0: 2.4 -> 2, 2.5 -> 3
    return floor(Fraction(x) + Fraction(1, 2))


def late_fee(amount, days_late):
    """คืนค่าปรับเป็นจำนวนเต็มสตางค์"""
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if type(days_late) is not int:
        raise ValueError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not (0 <= days_late <= MAX_DAYS):
        raise ValueError("days_late ต้องอยู่ระหว่าง 0 ถึง 365")

    if days_late <= GRACE_DAYS:
        return 0

    fee = Fraction(amount) * DAILY_RATE * days_late
    cap = Fraction(amount) * CAP_RATE
    if fee > cap:
        fee = cap
    return _half_up(fee)


def main():
    try:
        raw = sys.stdin.read()
        args = json.loads(raw)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = late_fee(**args)
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
