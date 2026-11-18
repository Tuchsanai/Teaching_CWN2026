import json
import sys

# rate in per-mille: silver 1.5%, gold 2.5%, platinum 4%
_RATES = {"silver": 15, "gold": 25, "platinum": 40}
_MIN_AMOUNT = 10000   # 100 baht, in satang
_CAP = 20000          # 200 baht per bill, in satang


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative int (satang)")
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < _MIN_AMOUNT:
        return 0
    mult = 2 if birthday and tier in ("gold", "platinum") else 1
    # exact integer math, single rounding at the end (floor per policy)
    value = amount * _RATES[tier] * mult // 1000
    return min(value, _CAP)


def main():
    try:
        data = json.load(sys.stdin)
        result = cashback(data["amount"], data["tier"], data["birthday"])
        print(json.dumps({"cashback": result}))
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
