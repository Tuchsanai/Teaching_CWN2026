"""BaanKafe cashback calculator.

กติกา (ยอดเป็นสตางค์):
- amount: ยอดซื้อ จำนวนเต็ม >= 0 (สตางค์)
- tier: "silver" 1.5%, "gold" 2.5%, "platinum" 4%
- birthday: True = ซื้อในเดือนเกิด ได้เงินคืน 2 เท่า
- ยอดซื้อต่ำกว่า 100 บาท (10000 สตางค์) ไม่ได้เงินคืน
- เงินคืนสูงสุด 200 บาท (20000 สตางค์) ต่อบิล (จำกัดหลังคูณ 2 เท่าแล้ว)
- ปัดลงเป็นจำนวนเต็มสตางค์ (ร้านจ่ายคืนให้ลูกค้า ไม่ให้จ่ายเกิน)
- คำนวณด้วย Fraction ปัดครั้งเดียวตอนท้าย
"""

import json
import sys
from fractions import Fraction
from math import floor

MIN_AMOUNT_SATANG = 10000      # 100 บาท
MAX_CASHBACK_SATANG = 20000    # 200 บาท
RATES_PERCENT = {"silver": 1.5, "gold": 2.5, "platinum": 4}


def cashback(amount, tier, birthday):
    # --- ตรวจ input แบบเข้มงวด ---
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็น int (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if type(tier) is not str:
        raise ValueError("tier ต้องเป็น str")
    if tier not in RATES_PERCENT:
        raise ValueError(f"tier ไม่รู้จัก: {tier!r}")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น bool")

    # --- ยอดต่ำกว่าเกณฑ์ ไม่ได้เงินคืน ---
    if amount < MIN_AMOUNT_SATANG:
        return 0

    # --- คำนวณใน Fraction ปัดครั้งเดียวตอนท้าย ---
    rate = Fraction(str(RATES_PERCENT[tier])) / 100
    value = Fraction(amount) * rate
    if birthday:
        value *= 2
    value = min(value, Fraction(MAX_CASHBACK_SATANG))
    return floor(value)  # ปัดลง


def main():
    try:
        args = json.loads(sys.stdin.read())
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = cashback(**args)
    except (ValueError, TypeError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
