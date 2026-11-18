import json
import sys
from fractions import Fraction


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if not isinstance(member, bool):
        raise ValueError("member must be a bool")
    total = 0
    for it in items:
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise ValueError("invalid item")
        price, qty = it["price"], it["qty"]
        if not _is_int(price) or not _is_int(qty):
            raise ValueError("price and qty must be int")
        if price < 0 or qty < 1:
            raise ValueError("price must be >= 0 and qty >= 1")
        total += price * qty
    amount = Fraction(total)
    if total >= 50000:  # 500 baht
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)
    n, d = amount.numerator, amount.denominator
    return (2 * n + d) // (2 * d)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(data["items"], data["member"])
    except (ValueError, KeyError, TypeError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e) or e.__class__.__name__}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
