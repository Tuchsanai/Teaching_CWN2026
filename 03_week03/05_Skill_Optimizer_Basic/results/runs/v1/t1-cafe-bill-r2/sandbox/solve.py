import json
import sys


def _is_int(v):
    return type(v) is int


def cafe_bill(items, member):
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if type(member) is not bool:
        raise ValueError("member must be a bool")
    total = 0
    for it in items:
        if not isinstance(it, dict):
            raise ValueError("each item must be a dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("item requires price and qty")
        p, q = it["price"], it["qty"]
        if not _is_int(p) or p < 0:
            raise ValueError("price must be a non-negative int")
        if not _is_int(q) or q < 1:
            raise ValueError("qty must be an int >= 1")
        total += p * q
    num, den = total, 1
    if total >= 50000:  # 500 baht
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    # single exact rounding at the end, half up
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("items", "member"):
            if k not in data:
                raise ValueError("missing key: " + k)
        result = cafe_bill(data["items"], data["member"])
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
