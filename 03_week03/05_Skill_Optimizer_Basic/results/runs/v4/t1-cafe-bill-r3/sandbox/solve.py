import json
import sys

THRESHOLD = 50000  # 500 บาท เป็นสตางค์


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
    num = total * 107
    den = 100
    if total >= THRESHOLD:
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    # half-up ครั้งเดียวตอนท้าย (จำนวนเต็มล้วน)
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be an object")
        result = cafe_bill(data.get("items"), data.get("member"))
        print(json.dumps({"ok": True, "result": result}))
    except (ValueError, TypeError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)


if __name__ == "__main__":
    main()
