"""BaanKafe cashback (หน่วยเงิน: สตางค์)"""
import json
import sys
from fractions import Fraction

RATES = {"silver": Fraction(3, 200), "gold": Fraction(5, 200), "platinum": Fraction(4, 100)}
MIN_AMOUNT = 10000   # 100 บาท
CAP = 20000          # 200 บาท
# สมมติฐานตามนโยบายร้าน: โบนัสเดือนเกิดใช้กับ gold/platinum เท่านั้น
BIRTHDAY_TIERS = {"gold", "platinum"}


def round_down(x):
    return int(Fraction(x) // 1)


def need_int(value, name, low=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def cashback(amount, tier, birthday):
    need_int(amount, "amount", 0)
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ไม่ถูกต้อง")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES[tier]
    if birthday and tier in BIRTHDAY_TIERS:
        rate *= 2
    return min(round_down(Fraction(amount) * rate), CAP)


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
