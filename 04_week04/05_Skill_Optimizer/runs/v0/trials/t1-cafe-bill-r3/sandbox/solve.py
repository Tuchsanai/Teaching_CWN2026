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
            raise ValueError("each item needs price and qty")
        p, q = it["price"], it["qty"]
        if not _is_int(p) or p < 0:
            raise ValueError("price must be a non-negative integer (satang)")
        if not _is_int(q) or q < 1:
            raise ValueError("qty must be an integer >= 1")
        total += p * q

    # เลขสัดส่วนแบบจำนวนเต็ม ปัดเศษครั้งเดียวตอนท้าย (half up)
    num, den = total, 1
    if total >= THRESHOLD:
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        out = {"total": cafe_bill(data.get("items"), data.get("member", False))}
        code = 0
    except (ValueError, json.JSONDecodeError) as e:
        out, code = {"error": str(e)}, 1
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(code)


if __name__ == "__main__":
    main()
