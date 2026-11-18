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
        if not isinstance(it, dict):
            raise ValueError("each item must be a dict")
        price = it.get("price")
        qty = it.get("qty")
        if not _is_int(price) or price < 0:
            raise ValueError("price must be a non-negative int (satang)")
        if not _is_int(qty) or qty < 1:
            raise ValueError("qty must be an int >= 1")
        total += price * qty

    amount = Fraction(total)
    if total >= 50000:  # 500 baht, compared before any discount
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)  # VAT last

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
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e) or e.__class__.__name__}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
