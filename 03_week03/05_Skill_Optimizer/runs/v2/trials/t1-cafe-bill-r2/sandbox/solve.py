import json
import sys


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    if not isinstance(member, bool):
        raise ValueError("member must be bool")
    if not isinstance(items, list) or not items:
        raise ValueError("items must be a non-empty list")
    total = 0
    for it in items:
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise ValueError("invalid item")
        p, q = it["price"], it["qty"]
        if not _is_int(p) or not _is_int(q) or p < 0 or q < 1:
            raise ValueError("invalid price/qty")
        total += p * q
    num, den = 1, 1
    if total >= 50000:
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    # exact integer arithmetic, round half up once at the end
    return (total * num * 2 + den) // (den * 2)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(data["items"], data["member"])
        print(json.dumps({"ok": True, "result": result}))
        return 0
    except (ValueError, KeyError, TypeError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": "invalid input: %s" % e}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
