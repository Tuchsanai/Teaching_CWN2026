import json
import sys
from fractions import Fraction


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def bulk_price(unit_price, qty, coupon):
    if not _is_int(unit_price) or unit_price < 0:
        raise ValueError("unit_price must be an int >= 0")
    if not _is_int(qty) or not 1 <= qty <= 1000:
        raise ValueError("qty must be an int in 1..1000")
    if not isinstance(coupon, bool):
        raise ValueError("coupon must be a bool")

    total = Fraction(unit_price * qty)
    if qty >= 50:
        total *= Fraction(1000 - 75, 1000)
    elif qty >= 10:
        total *= Fraction(1000 - 35, 1000)
    if coupon:
        total *= Fraction(1000 - 25, 1000)
    total *= Fraction(107, 100)
    n, d = total.numerator, total.denominator
    return (2 * n + d) // (2 * d)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = bulk_price(data["unit_price"], data["qty"], data["coupon"])
    except KeyError as e:
        print(json.dumps({"ok": False, "error": "missing key: %s" % e.args[0]}))
        return 2
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e) or "invalid input"}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
