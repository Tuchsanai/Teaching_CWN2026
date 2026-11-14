"""BaanKafe cashback (หน่วยสตางค์ ใช้ Fraction ไม่มี float)"""
import json
import sys
from fractions import Fraction

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
MIN_AMOUNT = 10000   # 100 บาท
CAP = 20000          # 200 บาท


def round_down(x):
    return int(Fraction(x) // 1)


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount ต้องเป็นจำนวนเต็มตั้งแต่ 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ไม่ถูกต้อง")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")
    if amount < MIN_AMOUNT:
        return 0
    x = Fraction(amount) * RATES[tier]
    if birthday:
        x *= 2
    return min(round_down(x), CAP)


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
