import json
import sys

_RATES = {"silver": 15, "gold": 25, "platinum": 40}  # per 1000
_MIN_AMOUNT = 10000  # 100 baht in satang
_CAP = 20000         # 200 baht in satang


def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x


def _flag(x):
    if not isinstance(x, bool):
        raise ValueError(f"expected bool, got {x!r}")
    return x


def cashback(amount, tier, birthday):
    amount = _int(amount, lo=0)
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError(f"invalid tier: {tier!r}")
    birthday = _flag(birthday)
    if amount < _MIN_AMOUNT:
        return 0
    num = amount * _RATES[tier] * (2 if birthday else 1)
    den = 1000
    result = (num * 2 + den) // (den * 2)  # half up, once
    return min(result, _CAP)


def _main():
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
    _main()
