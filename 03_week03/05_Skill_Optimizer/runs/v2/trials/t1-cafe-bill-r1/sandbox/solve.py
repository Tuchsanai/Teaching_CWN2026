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
            raise ValueError("invalid item")
        p, q = it["price"], it["qty"]
        if not _is_int(p) or p < 0:
            raise ValueError("invalid price")
        if not _is_int(q) or q < 1:
            raise ValueError("invalid qty")
        total += p * q
    num, den = total, 1
    if total >= 50000:  # 500 baht
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    # exact integer arithmetic, round half up once at the end
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(data["items"], data["member"])
        print(json.dumps({"ok": True, "result": result}))
    except (ValueError, KeyError) as e:
        print(json.dumps({"ok": False, "error": "missing key %s" % e if isinstance(e, KeyError) else str(e)}))
        sys.exit(2)


if __name__ == "__main__":
    main()
