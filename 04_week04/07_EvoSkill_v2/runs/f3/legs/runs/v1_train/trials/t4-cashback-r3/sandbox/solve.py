"""BaanKafe cashback (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
MIN_AMOUNT = 10000   # 100 บาท
CAP = 20000          # 200 บาท/บิล


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
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")
    if amount < MIN_AMOUNT:
        return 0
    x = Fraction(amount) * RATES[tier]
    # นโยบาย C1 (จากสกิล baankafe-known-policies): เดือนเกิด x2 เฉพาะ gold/platinum, silver ไม่ได้
    if birthday and tier != "silver":
        x *= 2
    # นโยบาย C2: เงินที่ร้านจ่ายออก -> ปัดลง แล้วจึงใช้เพดาน
    return min(CAP, round_down(x))


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
