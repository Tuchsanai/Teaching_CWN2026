"""BaanKafe cashback calculator.

กติกา:
- amount   : ยอดซื้อเป็นสตางค์ (int, ตั้งแต่ 0)
- tier     : "silver" 1.5% · "gold" 2.5% · "platinum" 4%
- birthday : True = ซื้อในเดือนเกิด ได้เงินคืน 2 เท่า
- ยอดซื้อต่ำกว่า 100 บาท (10000 สตางค์) ไม่ได้เงินคืน
- เงินคืนสูงสุด 200 บาท (20000 สตางค์) ต่อบิล (ตัดเพดานหลังคูณ 2 เท่าแล้ว)
- ผลเป็นจำนวนเต็มสตางค์ ปัดลง เพราะเป็นเงินที่ร้านจ่ายคืนลูกค้า
"""

import json
import sys
from fractions import Fraction
from math import floor

RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(40, 1000),  # 4%
}
MIN_AMOUNT = 100 * 100        # 100 บาท -> สตางค์
MAX_CASHBACK = 200 * 100      # 200 บาท -> สตางค์
BIRTHDAY_MULTIPLIER = 2


def cashback(amount, tier, birthday):
    """คืนค่าเงินคืนเป็นจำนวนเต็มสตางค์"""
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if type(tier) is not str:
        raise ValueError("tier ต้องเป็นสตริง")
    if tier not in RATES:
        raise ValueError("tier ไม่รู้จัก: %r" % tier)
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    if amount < MIN_AMOUNT:
        return 0

    value = Fraction(amount) * RATES[tier]
    if birthday:
        value *= BIRTHDAY_MULTIPLIER
    value = min(value, Fraction(MAX_CASHBACK))
    return floor(value)


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
