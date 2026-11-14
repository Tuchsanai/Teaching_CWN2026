# ค่าปรับลูกค้าขายส่งที่ชำระเงินช้า (BaanKafe)
#
# กติกา:
# 1. amount = ยอดค้างชำระ เป็นจำนวนเต็มสตางค์ ตั้งแต่ 0
# 2. days_late = จำนวนวันที่ช้า เป็นจำนวนเต็ม 0–365
# 3. ช้าไม่เกิน 3 วัน (days_late <= 3) ไม่คิดค่าปรับ
# 4. ช้าเกิน 3 วัน (days_late > 3) คิดวันละ 0.75% ของยอดค้างชำระ
#    นับทุกวันที่ช้า รวม 3 วันแรก (ไม่ใช่ days_late - 3)
# 5. ค่าปรับสูงสุดไม่เกิน 15% ของยอดค้างชำระ
# 6. ผลลัพธ์เป็นจำนวนเต็มสตางค์
#
# การปัด (เลือกเองตามสกิล money-rounding-satang; โจทย์ไม่ได้ระบุทิศทาง):
# - ค่าปรับเป็นยอดที่ลูกค้าต้องจ่าย จึงปัดครึ่งขึ้น (half_up) ครั้งเดียวตอนท้าย
# - เพดานปัดลง (floor) เพื่อไม่ให้ผลเกิน 15% ของยอดค้างชำระ แม้เพดานจะมีทศนิยม
#
# การคำนวณทั้งหมดใช้ Fraction ไม่ใช้ float

import json
import sys
from fractions import Fraction
from math import floor

GRACE_DAYS = 3
MAX_DAYS = 365
DAILY_RATE = Fraction(75, 10000)  # 0.75% ต่อวัน
CAP_RATE = Fraction(15, 100)      # เพดาน 15%


def _half_up(x):
    # ปัดครึ่งขึ้น: 2.4 -> 2, 2.5 -> 3 (x >= 0)
    return floor(Fraction(x) + Fraction(1, 2))


def late_fee(amount, days_late):
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if type(days_late) is not int:
        raise ValueError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ต่ำกว่า 0")
    if not (0 <= days_late <= MAX_DAYS):
        raise ValueError("days_late ต้องอยู่ระหว่าง 0 ถึง 365")

    if days_late <= GRACE_DAYS:
        return 0

    fee = Fraction(amount) * DAILY_RATE * days_late
    cap = Fraction(amount) * CAP_RATE

    # ปัดครั้งเดียวตอนท้าย; เพดานปัดลงเพื่อให้ไม่เกิน 15% จริง
    return min(_half_up(fee), floor(cap))


def main():
    try:
        raw = sys.stdin.read()
        args = json.loads(raw)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = late_fee(**args)
    except (ValueError, TypeError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    except json.JSONDecodeError as e:
        print(json.dumps({"ok": False, "error": f"JSON ไม่ถูกต้อง: {e}"}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
