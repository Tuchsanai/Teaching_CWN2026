from fractions import Fraction


def _int(x, name, lo=None):
    if type(x) is not int:
        raise ValueError(f"{name} must be an integer")
    if lo is not None and x < lo:
        raise ValueError(f"{name} out of range")
    return x


def cafe_bill(items, member):
    if type(member) is not bool:
        raise ValueError("member must be a boolean")
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    subtotal = 0
    for it in items:
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise ValueError("each item must be a dict with price and qty")
        price = _int(it["price"], "price", 0)
        qty = _int(it["qty"], "qty", 1)
        subtotal += price * qty

    total = Fraction(subtotal)
    if subtotal >= 50000:  # 500 baht, in satang
        total *= Fraction(95, 100)
    if member:
        total *= Fraction(90, 100)
    total *= Fraction(107, 100)
    # half-up rounding, once at the end
    return (2 * total.numerator + total.denominator) // (2 * total.denominator)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(**data)
        print(json.dumps({"ok": True, "result": result}))
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
