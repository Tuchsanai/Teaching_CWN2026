"""BaanKafe: late fee for wholesale customers.

กติกา:
- amount = ยอดค้างชำระ (สตางค์, int >= 0)
- days_late = จำนวนวันที่ช้า (int 0..365)
- ช้าไม่เกิน 3 วัน -> ค่าปรับ 0
- ช้าเกิน 3 วัน -> ค่าปรับ = 0.75% ต่อวัน ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- เพดาน = 15% ของยอดค้างชำระ
- คืนค่าปรับเป็นจำนวนเต็มสตางค์

การคำนวณ:
- ใช้ Fraction ตลอดทาง ไม่ใช้ float
- ปัดครึ่งขึ้นครั้งเดียวตอนท้าย (ยอดที่ลูกค้าต้องจ่ายตามสกิล money-rounding-satang)
- เพดานใช้ floor ของ 15% เพื่อให้ผลไม่เกิน 15% เสมอ
"""

import json
import sys
from fractions import Fraction
from math import floor

GRACE_DAYS = 3
DAILY_RATE_NUM = 75        # 0.75% = 75 / 10000
DAILY_RATE_DEN = 10000
CAP_NUM = 15               # 15% = 15 / 100
CAP_DEN = 100
MAX_DAYS = 365


def _half_up(x):
    # ปัดครึ่งขึ้น สำหรับ x >= 0: 2.4 -> 2, 2.5 -> 3
    return floor(Fraction(x) + Fraction(1, 2))


def late_fee(amount, days_late):
    # ตรวจชนิดแบบเข้มงวด: bool, float, str ต้องถูก reject
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

    raw_fee = Fraction(amount * DAILY_RATE_NUM * days_late, DAILY_RATE_DEN)
    fee = _half_up(raw_fee)

    cap = floor(Fraction(amount * CAP_NUM, CAP_DEN))
    return min(fee, cap)


def main():
    try:
        raw = sys.stdin.read()
        args = json.loads(raw)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = late_fee(**args)
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
