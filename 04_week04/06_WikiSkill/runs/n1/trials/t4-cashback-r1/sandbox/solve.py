import json
import sys

_RATES = {"silver": (3, 200), "gold": (1, 40), "platinum": (1, 25)}
_MIN_AMOUNT = 10000  # 100 baht in satang
_CAP = 20000         # 200 baht in satang


def _int(x, name, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"{name} must be an integer")
    if lo is not None and x < lo:
        raise ValueError(f"{name} must be >= {lo}")
    if hi is not None and x > hi:
        raise ValueError(f"{name} must be <= {hi}")
    return x


def _flag(x, name):
    if not isinstance(x, bool):
        raise ValueError(f"{name} must be a bool")
    return x


def cashback(amount, tier, birthday):
    _int(amount, "amount", lo=0)
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError("tier must be one of: silver, gold, platinum")
    _flag(birthday, "birthday")

    if amount < _MIN_AMOUNT:
        return 0
    n, d = _RATES[tier]
    if birthday:
        n *= 2
    num = amount * n
    # half up, rounded once
    value = (2 * num + d) // (2 * d)
    return min(value, _CAP)


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
