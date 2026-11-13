"""คำนวณเงินคืนสมาชิกของ BaanKafe

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม)
"""
import json
import sys
from fractions import Fraction

# อัตราเงินคืนต่อระดับสมาชิก
RATES = {
    "silver": Fraction("1.5") / 100,
    "gold": Fraction("2.5") / 100,
    "platinum": Fraction("4") / 100,
}
MIN_AMOUNT = 100 * 100        # ยอดซื้อขั้นต่ำ 100 บาท (ต่ำกว่านี้ไม่ได้เงินคืน)
MAX_CASHBACK = 200 * 100      # เงินคืนสูงสุด 200 บาทต่อบิล
BIRTHDAY_MULTIPLIER = 2       # ซื้อในเดือนเกิด ได้เงินคืน 2 เท่า


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม รับ int หรือ Fraction ที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def cashback(amount, tier, birthday):
    """คืนเงินคืนเป็นจำนวนเต็มสตางค์

    amount   : ยอดซื้อ (สตางค์ จำนวนเต็ม ตั้งแต่ 0)
    tier     : "silver", "gold" หรือ "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด
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

    # เก็บเป็นเศษส่วนทุกขั้น ปัดครั้งเดียวตอนท้าย
    value = Fraction(amount) * RATES[tier]
    if birthday:
        value *= BIRTHDAY_MULTIPLIER
    value = min(value, MAX_CASHBACK)
    return _half_up(value)


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
