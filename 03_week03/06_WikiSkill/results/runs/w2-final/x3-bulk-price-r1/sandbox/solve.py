import json
import sys


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


def bulk_price(unit_price, qty, coupon):
    unit_price = _int(unit_price, lo=0)
    qty = _int(qty, lo=1, hi=1000)
    coupon = _flag(coupon)

    # rates in per-mille
    if qty >= 50:
        d = 75
    elif qty >= 10:
        d = 35
    else:
        d = 0
    c = 25 if coupon else 0

    num = unit_price * qty * (1000 - d) * (1000 - c) * 107
    den = 1000 * 1000 * 100
    return (num * 2 + den) // (den * 2)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = bulk_price(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
