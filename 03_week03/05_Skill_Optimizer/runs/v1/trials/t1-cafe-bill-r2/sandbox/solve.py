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
            raise ValueError("each item must be a dict with price and qty")
        p, q = it["price"], it["qty"]
        if not _is_int(p) or p < 0:
            raise ValueError("price must be a non-negative int")
        if not _is_int(q) or q < 1:
            raise ValueError("qty must be an int >= 1")
        total += p * q
    # exact integer arithmetic: numerator / denominator
    num, den = total, 1
    if total >= 50000:
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (2 * num + den) // (2 * den)  # round half up


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        if "items" not in data or "member" not in data:
            raise ValueError("missing key")
        result = cafe_bill(data["items"], data["member"])
        print(json.dumps({"ok": True, "result": result}))
        return 0
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
