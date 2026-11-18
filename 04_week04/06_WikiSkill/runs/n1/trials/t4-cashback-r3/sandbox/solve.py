import json
import sys
from fractions import Fraction

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
MIN_AMOUNT = 10000   # 100 baht in satang
CAP = 20000          # 200 baht in satang


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("amount must be an integer")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not isinstance(tier, str) or tier not in RATES:
        raise ValueError("tier must be one of silver, gold, platinum")
    if not isinstance(birthday, bool):
        raise ValueError("birthday must be a bool")
    if amount < MIN_AMOUNT:
        return 0
    value = amount * RATES[tier] * (2 if birthday else 1)
    num, den = value.numerator, value.denominator
    result = (2 * num + den) // (2 * den)  # half up, once
    return min(result, CAP)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cashback(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
