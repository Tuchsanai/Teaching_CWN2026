"""BaanKafe cashback (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
MIN_AMOUNT = 10000   # 100 บาท
CAP = 20000          # 200 บาท


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
    value = Fraction(amount) * RATES[tier]
    # นโยบายร้าน (house-rules C1): เดือนเกิด x2 เฉพาะ gold/platinum, silver ไม่ได้สิทธิ์
    if birthday and tier != "silver":
        value *= 2
    # นโยบายร้าน (C2): เงินที่ร้านจ่ายออก ปัดทิ้ง แล้วค่อยใช้ cap
    return min(CAP, int(value // 1))


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
