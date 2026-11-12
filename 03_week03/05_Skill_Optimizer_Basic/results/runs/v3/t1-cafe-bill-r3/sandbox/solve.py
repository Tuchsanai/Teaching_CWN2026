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
            raise ValueError("item needs price and qty")
        price, qty = it["price"], it["qty"]
        if not _is_int(price) or not _is_int(qty):
            raise ValueError("price and qty must be int")
        if price < 0 or qty < 1:
            raise ValueError("price must be >= 0 and qty >= 1")
        total += price * qty
    num = total
    den = 1
    if total >= 50000:
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    num *= 107
    den *= 100
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        if "items" not in data or "member" not in data:
            raise ValueError("missing key")
        result = cafe_bill(data["items"], data["member"])
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
