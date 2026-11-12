from fractions import Fraction


def _int(x, name, lo=None, hi=None):
    if type(x) is not int:
        raise ValueError(f"{name} must be an integer")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"{name} out of range")
    return x


def _bool(x, name):
    if type(x) is not bool:
        raise ValueError(f"{name} must be a boolean")
    return x


def bulk_price(unit_price, qty, coupon):
    _int(unit_price, "unit_price", 0)
    _int(qty, "qty", 1, 1000)
    _bool(coupon, "coupon")
    total = Fraction(unit_price * qty)
    if qty >= 50:
        total *= Fraction(925, 1000)
    elif qty >= 10:
        total *= Fraction(965, 1000)
    if coupon:
        total *= Fraction(975, 1000)
    total *= Fraction(107, 100)
    # half-up rounding once at the end
    return (2 * total.numerator + total.denominator) // (2 * total.denominator)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = bulk_price(**data)
        print(json.dumps({"ok": True, "result": result}))
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
