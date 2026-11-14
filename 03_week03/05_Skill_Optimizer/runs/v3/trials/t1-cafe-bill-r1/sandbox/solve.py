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
        p, q = it["price"], it["qty"]
        if not _is_int(p) or p < 0:
            raise ValueError("invalid price")
        if not _is_int(q) or q < 1:
            raise ValueError("invalid qty")
        total += p * q
    amt = Fraction(total)
    if total >= 50000:
        amt = amt * 95 / 100
    if member:
        amt = amt * 90 / 100
    amt = amt * 107 / 100
    n, d = amt.numerator, amt.denominator
    return (2 * n + d) // (2 * d)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be an object")
        if "items" not in data or "member" not in data:
            raise ValueError("missing key")
        out = {"ok": True, "result": cafe_bill(data["items"], data["member"])}
        code = 0
    except Exception as e:
        out = {"ok": False, "error": str(e) or "invalid input"}
        code = 2
    print(json.dumps(out))
    sys.exit(code)


if __name__ == "__main__":
    main()
