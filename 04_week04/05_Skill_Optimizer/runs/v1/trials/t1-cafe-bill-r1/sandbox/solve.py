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
            raise ValueError("price must be an int >= 0")
        if not _is_int(q) or q < 1:
            raise ValueError("qty must be an int >= 1")
        total += p * q
    num, den = total, 1
    if total >= 50000:
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    # ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย ด้วยจำนวนเต็มล้วน
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        if "items" not in data or "member" not in data:
            raise ValueError("missing key")
        result = cafe_bill(data["items"], data["member"])
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e) or "invalid input"}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
