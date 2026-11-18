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
    num, den = total, 1
    if total >= 50000:
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (2 * num + den) // (2 * den)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        if "items" not in data or "member" not in data:
            raise ValueError("missing key")
        out = {"ok": True, "result": cafe_bill(data["items"], data["member"])}
        code = 0
    except Exception as e:
        out = {"ok": False, "error": str(e) or "invalid input"}
        code = 2
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(code)


if __name__ == "__main__":
    _main()
