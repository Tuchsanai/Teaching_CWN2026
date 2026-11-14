"""BaanKafe cashback calculator.

กติกา (ยอดทุกค่าเป็นสตางค์ จำนวนเต็ม):
- amount  : ยอดซื้อ เป็น int ตั้งแต่ 0 (สตางค์)
- tier    : "silver" (1.5%), "gold" (2.5%), "platinum" (4%)
- birthday: True = ซื้อในเดือนเกิด ได้เงินคืน 2 เท่า
- ยอดซื้อต่ำกว่า 100 บาท (10000 สตางค์) ไม่ได้เงินคืน
- เงินคืนสูงสุด 200 บาท (20000 สตางค์) ต่อบิล (ใช้หลังคูณ 2 เท่าเดือนเกิดแล้ว)
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ ปัดลง (เงินที่ร้านจ่ายคืนให้ลูกค้า)

การคำนวณใช้ Fraction ตลอดทาง ปัดครั้งเดียวตอนท้ายสุด ไม่ใช้ float
"""

import json
import sys
from fractions import Fraction
from math import floor

MIN_AMOUNT_SATANG = 100 * 100      # 100 บาท
MAX_CASHBACK_SATANG = 200 * 100    # 200 บาท ต่อบิล
BIRTHDAY_MULTIPLIER = 2

RATE_PERCENT = {
    "silver": Fraction(15, 10),    # 1.5%
    "gold": Fraction(25, 10),      # 2.5%
    "platinum": Fraction(4, 1),    # 4%
}


def cashback(amount, tier, birthday):
    # --- ตรวจ input แบบเข้มงวด ---
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็น int (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if type(tier) is not str or tier not in RATE_PERCENT:
        raise ValueError("tier ต้องเป็น 'silver', 'gold' หรือ 'platinum'")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    # --- ยอดต่ำกว่าเกณฑ์ไม่ได้เงินคืน ---
    if amount < MIN_AMOUNT_SATANG:
        return 0

    # --- คำนวณ: ยอด × อัตรา × (2 ถ้าเดือนเกิด) แล้วเพดาน แล้วปัดลงครั้งเดียว ---
    rate = RATE_PERCENT[tier] / 100
    value = Fraction(amount) * rate
    if birthday:
        value *= BIRTHDAY_MULTIPLIER
    value = min(value, Fraction(MAX_CASHBACK_SATANG))
    return floor(value)


def main():
    try:
        args = json.loads(sys.stdin.read())
        if type(args) is not dict:
            raise ValueError("input ต้องเป็น JSON object")
        result = cashback(**args)
    except (ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
