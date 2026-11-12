import json
import sys


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
            raise ValueError("item must be a dict with price and qty")
        price, qty = it["price"], it["qty"]
        if not _is_int(price) or price < 0:
            raise ValueError("price must be a non-negative int")
        if not _is_int(qty) or qty < 1:
            raise ValueError("qty must be an int >= 1")
        total += price * qty
    num, den = 107, 100  # VAT 7%
    if total >= 50000:  # 500 baht
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    # single half-up rounding at the end, integers only
    return (2 * total * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(data.get("items"), data.get("member", False))
        print(json.dumps({"ok": True, "result": result}))
    except (ValueError, TypeError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)


if __name__ == "__main__":
    main()
