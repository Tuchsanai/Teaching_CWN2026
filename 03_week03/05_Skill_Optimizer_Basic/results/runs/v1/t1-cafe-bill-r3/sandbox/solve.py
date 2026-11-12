import json
import sys


def _is_int(v):
    return type(v) is int


def cafe_bill(items, member):
    if not isinstance(items, list) or not items:
        raise ValueError("items must be a non-empty list")
    if type(member) is not bool:
        raise ValueError("member must be bool")
    total = 0
    for it in items:
        if not isinstance(it, dict):
            raise ValueError("item must be a dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("item needs price and qty")
        p, q = it["price"], it["qty"]
        if not _is_int(p) or not _is_int(q):
            raise ValueError("price and qty must be int")
        if p < 0 or q < 1:
            raise ValueError("price must be >= 0 and qty >= 1")
        total += p * q
    num, den = 1, 1
    if total >= 50000:
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    # single rounding at the end, half up, integers only
    return (total * num * 2 + den) // (den * 2)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        if "items" not in data or "member" not in data:
            raise ValueError("missing key")
        result = cafe_bill(data["items"], data["member"])
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e) or "invalid input"}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
