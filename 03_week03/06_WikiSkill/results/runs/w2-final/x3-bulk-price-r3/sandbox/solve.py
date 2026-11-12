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

    num = unit_price * qty
    den = 1
    if qty >= 50:
        num *= 925
        den *= 1000
    elif qty >= 10:
        num *= 965
        den *= 1000
    if coupon:
        num *= 975
        den *= 1000
    num *= 107
    den *= 100
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
