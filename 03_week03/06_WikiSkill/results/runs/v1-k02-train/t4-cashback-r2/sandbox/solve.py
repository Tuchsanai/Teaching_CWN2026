import json
import sys

_RATES = {"silver": 15, "gold": 25, "platinum": 40}  # per 1000
_MIN_AMOUNT = 10000   # 100 baht in satang
_CAP = 20000          # 200 baht in satang


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be int >= 0")
    if type(tier) is not str or tier not in _RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < _MIN_AMOUNT:
        return 0
    n = amount * _RATES[tier] * (2 if birthday else 1)
    d = 1000
    return min((2 * n + d) // (2 * d), _CAP)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = cashback(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
