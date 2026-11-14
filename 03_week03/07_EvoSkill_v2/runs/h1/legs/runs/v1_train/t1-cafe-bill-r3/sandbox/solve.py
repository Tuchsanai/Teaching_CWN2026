"""BaanKafe cashier bill calculator.

Rules (from the spec):
- items: list of {"price": satang per piece (int), "qty": pieces (int, >= 1)}
- subtotal >= 500 baht (50000 satang)  -> 5% discount
- member is True                        -> further 10% discount (applied to the
                                           already-discounted amount)
- VAT 7% added last, on the discounted amount
- Result: amount customer pays, integer satang
Arithmetic uses Fraction; the only rounding is half-up, applied once at the end.
"""

import json
import sys
from fractions import Fraction
from math import floor

THRESHOLD_SATANG = 50000  # 500 baht
VOLUME_DISCOUNT = Fraction(5, 100)
MEMBER_DISCOUNT = Fraction(10, 100)
VAT_RATE = Fraction(7, 100)


def _half_up(x):
    # x >= 0; 2.4 -> 2, 2.5 -> 3
    return floor(Fraction(x) + Fraction(1, 2))


def _is_plain_int(v):
    return type(v) is int


def cafe_bill(items, member):
    if type(member) is not bool:
        raise ValueError("member must be bool")
    if type(items) is not list:
        raise ValueError("items must be a list")

    subtotal = 0
    for item in items:
        if type(item) is not dict:
            raise ValueError("each item must be a dict")
        if "price" not in item or "qty" not in item:
            raise ValueError("each item needs 'price' and 'qty'")
        price = item["price"]
        qty = item["qty"]
        if not _is_plain_int(price) or price < 0:
            raise ValueError("price must be an int satang >= 0")
        if not _is_plain_int(qty) or qty < 1:
            raise ValueError("qty must be an int >= 1")
        subtotal += price * qty

    total = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:
        total *= 1 - VOLUME_DISCOUNT
    if member:
        total *= 1 - MEMBER_DISCOUNT
    total *= 1 + VAT_RATE

    return _half_up(total)


def main():
    try:
        args = json.load(sys.stdin)
        if type(args) is not dict:
            raise ValueError("stdin must be a JSON object")
        result = cafe_bill(**args)
    except (ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
