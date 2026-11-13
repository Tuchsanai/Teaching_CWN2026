"""BaanKafe cashback calculator.

ยอดซื้อและเงินคืนทั้งหมดเป็นสตางค์ (จำนวนเต็ม)
"""
import json
import sys
from fractions import Fraction

MIN_AMOUNT = 10000   # 100 บาท ต่ำกว่านี้ไม่ได้เงินคืน
CAP = 20000          # เพดานเงินคืนต่อบิล 200 บาท
RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(40, 1000),  # 4%
}


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def cashback(amount, tier, birthday):
    """คืนค่าเงินคืนเป็นสตางค์ (int)

    amount   : ยอดซื้อ (สตางค์ int ตั้งแต่ 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด (ได้เงินคืน 2 เท่า)
    """
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    if amount < MIN_AMOUNT:
        return 0

    value = Fraction(amount) * RATES[tier]   # ไม่ปัดระหว่างทาง
    if birthday:
        value *= 2
    return min(_half_up(value), CAP)         # ปัดครั้งเดียว แล้วจำกัดเพดาน


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = cashback(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
