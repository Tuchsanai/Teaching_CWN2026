"""BaanKafe cashback (หน่วยสตางค์)
สมมติฐานตามนโยบายร้าน: โบนัสเดือนเกิด x2 ใช้กับ gold/platinum เท่านั้น (silver ไม่ได้),
เงินคืนเป็นเงินที่ร้านจ่ายออก -> ปัดลง, เพดาน 200 บาท = 20000 สตางค์ ใช้หลังคูณ 2"""
import json
import sys
from fractions import Fraction

RATES = {"silver": Fraction(3, 200), "gold": Fraction(1, 40), "platinum": Fraction(1, 25)}
BIRTHDAY_TIERS = ("gold", "platinum")
MIN_AMOUNT = 10000
CAP = 20000


def round_down(x):
    return int(Fraction(x) // 1)


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม >= 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ไม่ถูกต้อง")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")
    if amount < MIN_AMOUNT:
        return 0
    value = amount * RATES[tier]
    if birthday and tier in BIRTHDAY_TIERS:
        value *= 2
    return min(round_down(value), CAP)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = cashback(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
