import json
import sys


def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x


def late_fee(amount, days_late):
    amount = _int(amount, lo=0)
    days_late = _int(days_late, lo=0, hi=365)
    if days_late <= 3:
        return 0
    # fee = amount * 0.75% * days = amount*3*days/400 ; cap = amount*15% = amount*3/20
    num = min(amount * 3 * days_late * 1, amount * 60)  # cap 3/20 = 60/400
    den = 400
    return (num * 2 + den) // (den * 2)  # half up, once


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = late_fee(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
