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
            raise ValueError("each item must be a dict with price and qty")
        price, qty = it["price"], it["qty"]
        if not _is_int(price) or not _is_int(qty):
            raise ValueError("price and qty must be int")
        if price < 0 or qty < 1:
            raise ValueError("price must be >= 0 and qty >= 1")
        total += price * qty

    amount = Fraction(total)
    if total >= 50000:  # 500 baht, compared on exact total
        amount = amount * 95 / 100
    if member:
        amount = amount * 90 / 100
    amount = amount * 107 / 100  # VAT

    n, d = amount.numerator, amount.denominator
    return (2 * n + d) // (2 * d)  # round half up, once


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        if "items" not in data or "member" not in data:
            raise ValueError("missing key")
        result = cafe_bill(data["items"], data["member"])
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
