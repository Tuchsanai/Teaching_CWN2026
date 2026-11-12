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


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items must be a list")
    _bool(member, "member")
    total = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("each item must be a dict with price and qty")
        price = _int(it["price"], "price", 0)
        qty = _int(it["qty"], "qty", 1)
        total += price * qty
    amount = Fraction(total)
    if total >= 50000:  # 500 baht = 50000 satang
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)
    return (2 * amount.numerator + amount.denominator) // (2 * amount.denominator)


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
