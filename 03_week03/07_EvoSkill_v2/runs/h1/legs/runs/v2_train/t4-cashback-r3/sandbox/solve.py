"""BaanKafe cashback calculator.

กติกา (ทุกค่าเป็นสตางค์ เป็นจำนวนเต็ม):
- amount: ยอดซื้อ int >= 0 (สตางค์)
- tier: "silver" 1.5%, "gold" 2.5%, "platinum" 4% (ค่าอื่น -> ValueError)
- birthday: True = ซื้อในเดือนเกิด ได้เงินคืน 2 เท่า (ต้องเป็น bool)
- ยอดซื้อ < 100 บาท (10000 สตางค์) ไม่ได้เงินคืน (0)
- เงินคืนสูงสุด 200 บาท (20000 สตางค์) ต่อบิล
- ผลเป็นจำนวนเต็มสตางค์ ปัดลงครั้งเดียวตอนท้าย (ร้านจ่ายคืนลูกค้า จึงไม่จ่ายเกิน)
"""

import json
import sys
from fractions import Fraction
from math import floor

MIN_AMOUNT_SATANG = 10000   # 100 บาท
MAX_CASHBACK_SATANG = 20000  # 200 บาท
RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(40, 1000),  # 4%
}


def cashback(amount, tier, birthday):
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็น int (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น bool")

    if amount < MIN_AMOUNT_SATANG:
        return 0

    value = Fraction(amount) * RATES[tier]
    if birthday:
        value *= 2
    value = min(value, MAX_CASHBACK_SATANG)
    return floor(value)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = cashback(**args)
    except (ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
