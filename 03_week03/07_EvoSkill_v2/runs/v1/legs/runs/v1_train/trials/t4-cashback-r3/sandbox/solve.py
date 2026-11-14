import json
import sys
from fractions import Fraction

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
MIN_AMOUNT = 100 * 100   # 100 บาท เป็นสตางค์
CAP = 200 * 100          # 200 บาท เป็นสตางค์


def round_down(x):
    """ปัดลง — เงินคืนเป็นเงินที่ร้านจ่ายออก"""
    return int(Fraction(x) // 1)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def cashback(amount, tier, birthday):
    need_int(amount, "amount", 0)
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ไม่ถูกต้อง")
    need_bool(birthday, "birthday")

    if amount < MIN_AMOUNT:
        return 0
    value = Fraction(amount) * RATES[tier]
    # ตัวคูณเดือนเกิดใช้กับ gold/platinum เท่านั้น (ตามสกิลนโยบายร้าน)
    if birthday and tier != "silver":
        value *= 2
    value = min(value, Fraction(CAP))
    return round_down(value)


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
