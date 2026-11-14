import json
import sys
from fractions import Fraction

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
MIN_AMOUNT = 100 * 100   # 100 baht in satang (>= qualifies)
CAP = 200 * 100          # 200 baht per bill in satang
# Assumption (business default): birthday x2 bonus only for gold/platinum, not silver.
BIRTHDAY_TIERS = {"gold", "platinum"}


def need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def need_bool(v, name):
    if type(v) is not bool:
        raise ValueError(f"{name} ต้องเป็น True/False")
    return v


def cashback(amount, tier, birthday):
    need_int(amount, "amount", low=0)
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ไม่ถูกต้อง")
    need_bool(birthday, "birthday")

    if amount < MIN_AMOUNT:
        return 0
    rate = RATES[tier]
    if birthday and tier in BIRTHDAY_TIERS:
        rate *= 2
    # cashback is paid out by the shop -> floor; cap applied after rounding
    value = int(amount * rate // 1)
    return min(CAP, value)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = cashback(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
