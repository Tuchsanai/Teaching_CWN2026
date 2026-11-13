"""BaanKafe: คิดค่าปรับลูกค้าขายส่งที่ชำระเงินช้า

กติกา
- amount เป็นยอดค้างชำระหน่วยสตางค์ (int, ตั้งแต่ 0)
- days_late เป็นจำนวนวันที่ช้า (int, 0–365)
- ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน คิดวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุด 15% ของยอดค้างชำระ
- คืนค่าปรับเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น ปัดครั้งเดียวตอนท้าย)
"""

import json
import sys
from fractions import Fraction

GRACE_DAYS = 3                    # ช้าไม่เกินนี้ไม่คิดค่าปรับ
DAILY_RATE = Fraction(75, 10000)  # 0.75% ต่อวัน
MAX_RATE = Fraction(15, 100)      # เพดาน 15% ของยอดค้างชำระ
MAX_DAYS = 365


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม สำหรับค่า Fraction ที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def late_fee(amount, days_late):
    """คืนค่าปรับ (สตางค์, int) ของยอดค้างชำระ amount ที่ช้า days_late วัน"""
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่น้อยกว่า 0")
    if type(days_late) is not int:
        raise ValueError("days_late ต้องเป็นจำนวนเต็ม")
    if days_late < 0 or days_late > MAX_DAYS:
        raise ValueError("days_late ต้องอยู่ระหว่าง 0 ถึง 365")

    if days_late <= GRACE_DAYS:
        return 0

    principal = Fraction(amount)
    fee = principal * DAILY_RATE * days_late   # นับทุกวันที่ช้า รวม 3 วันแรก
    cap = principal * MAX_RATE                 # เพดาน 15%
    return _half_up(min(fee, cap))


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = late_fee(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
