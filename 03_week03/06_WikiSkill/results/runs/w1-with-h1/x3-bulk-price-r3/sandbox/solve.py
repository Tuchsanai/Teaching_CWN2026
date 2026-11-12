import sys
import json
from fractions import Fraction


def _half_up(x: Fraction) -> int:
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def _int(v, name, lo=None, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be an integer")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def _bool(v, name):
    if not isinstance(v, bool):
        raise ValueError(f"{name} must be a bool")
    return v


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
    return _half_up(total)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = bulk_price(**data)
        out = json.dumps({"ok": True, "result": result})
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
