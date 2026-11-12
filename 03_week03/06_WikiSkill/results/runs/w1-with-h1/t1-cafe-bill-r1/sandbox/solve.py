import sys
import json
from fractions import Fraction


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


def _half_up(x: Fraction) -> int:
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def cafe_bill(items, member):
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    _bool(member, "member")
    subtotal = 0
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            raise ValueError(f"items[{i}] must be a dict")
        if "price" not in it or "qty" not in it:
            raise ValueError(f"items[{i}] must have price and qty")
        price = _int(it["price"], f"items[{i}].price", 0)
        qty = _int(it["qty"], f"items[{i}].qty", 1)
        subtotal += price * qty
    total = Fraction(subtotal)
    if subtotal >= 50000:  # 500 baht, compared unrounded
        total *= Fraction(95, 100)
    if member:
        total *= Fraction(90, 100)
    total *= Fraction(107, 100)
    return _half_up(total)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(**data)
        out = json.dumps({"ok": True, "result": result})
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
