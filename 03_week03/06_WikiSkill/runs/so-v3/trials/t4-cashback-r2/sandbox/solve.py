import json
import sys
from fractions import Fraction

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(40, 1000)}
MIN_AMOUNT = 10000   # 100 บาท
CAP = 20000          # 200 บาท


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative int")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < MIN_AMOUNT:
        return 0
    value = amount * RATES[tier]
    if birthday and tier in ("gold", "platinum"):
        value *= 2
    value = min(value, CAP)
    # เงินคืนปัดลงเสมอ
    return value.numerator // value.denominator


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cashback(data["amount"], data["tier"], data["birthday"])
    except (ValueError, KeyError) as e:
        print(json.dumps({"ok": False, "error": "missing key %s" % e if isinstance(e, KeyError) else str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
