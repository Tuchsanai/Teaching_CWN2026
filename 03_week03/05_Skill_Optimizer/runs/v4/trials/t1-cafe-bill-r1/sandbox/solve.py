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
        if not _is_int(p) or not _is_int(q) or p < 0 or q < 1:
            raise ValueError("invalid price or qty")
        total += p * q
    num, den = 107, 100
    if total >= 50000:
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    # half-up rounding once at the end
    return (2 * total * num + den) // (2 * den)


def main(argv):
    try:
        raw = argv[1] if len(argv) > 1 else sys.stdin.read()
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("input must be an object")
        result = cafe_bill(data.get("items"), data.get("member"))
        print(json.dumps({"ok": True, "result": result}))
        return 0
    except (ValueError, TypeError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
