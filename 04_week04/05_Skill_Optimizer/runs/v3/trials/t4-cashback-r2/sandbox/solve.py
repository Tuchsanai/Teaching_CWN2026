import json
import sys
from fractions import Fraction

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(40, 1000)}
MIN_AMOUNT = 100 * 100  # สตางค์
CAP = 200 * 100  # สตางค์


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative int (satang)")
    if not isinstance(tier, str) or tier not in RATES:
        raise ValueError("tier must be silver, gold or platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday must be a bool")
    if amount < MIN_AMOUNT:
        return 0
    value = amount * RATES[tier]
    if birthday and tier in ("gold", "platinum"):
        value *= 2
    value = min(value, CAP)
    # เงินคืนเป็นเงินที่ร้านจ่ายออก: ปัดเศษลงเสมอ
    return value.numerator // value.denominator


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("amount", "tier", "birthday"):
            if k not in data:
                raise ValueError("missing key: " + k)
        result = cashback(data["amount"], data["tier"], data["birthday"])
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
