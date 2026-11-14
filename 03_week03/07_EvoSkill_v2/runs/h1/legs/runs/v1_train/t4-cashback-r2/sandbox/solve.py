"""BaanKafe cashback calculator.

กติกา (หน่วยเป็นสตางค์ 1 บาท = 100 สตางค์)
- amount: ยอดซื้อ เป็น int ตั้งแต่ 0 (สตางค์)
- tier: "silver" = 1.5%, "gold" = 2.5%, "platinum" = 4%
- ยอดซื้อต่ำกว่า 100 บาท (10000 สตางค์) ไม่ได้เงินคืน -> 0
- birthday = True (ซื้อในเดือนเกิด) -> เงินคืนเป็น 2 เท่า
- เงินคืนสูงสุด 200 บาท (20000 สตางค์) ต่อบิล (ตัดเพดานหลังคูณ 2 เท่าแล้ว)
- ผลเป็นจำนวนเต็มสตางค์ ปัดลง เพราะเป็นเงินที่ร้านจ่ายคืนให้ลูกค้า
"""

import json
import sys
from fractions import Fraction
from math import floor

MIN_AMOUNT = 10000  # 100 บาท
MAX_CASHBACK = 20000  # 200 บาท
RATES = {
    "silver": Fraction(15, 1000),  # 1.5%
    "gold": Fraction(25, 1000),  # 2.5%
    "platinum": Fraction(4, 100),  # 4%
}


def cashback(amount, tier, birthday):
    """คืนค่าเงินคืนสมาชิกเป็นจำนวนเต็มสตางค์"""
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็น int (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    if amount < MIN_AMOUNT:
        return 0

    value = Fraction(amount) * RATES[tier]
    if birthday:
        value *= 2
    return min(floor(value), MAX_CASHBACK)


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
