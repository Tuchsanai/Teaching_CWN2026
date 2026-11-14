"""BaanKafe cafe_bill: all money in integer satang, no floats."""
import json
import sys


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if not isinstance(member, bool):
        raise ValueError("member must be a bool")
    subtotal = 0
    for it in items:
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise ValueError("each item must be a dict with price and qty")
        p, q = it["price"], it["qty"]
        if not _is_int(p) or p < 0:
            raise ValueError("price must be a non-negative integer (satang)")
        if not _is_int(q) or q < 1:
            raise ValueError("qty must be an integer >= 1")
        subtotal += p * q

    num, den = subtotal, 1
    if subtotal >= 50000:  # 500 baht
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100  # VAT last
    # exact rational, round half up once at the end
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        total = cafe_bill(data.get("items"), data.get("member", False))
        print(json.dumps({"total": total}))
    except (ValueError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
