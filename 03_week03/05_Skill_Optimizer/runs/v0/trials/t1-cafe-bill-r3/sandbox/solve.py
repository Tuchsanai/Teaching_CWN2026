import json
import sys

THRESHOLD = 50000  # 500 บาท เป็นสตางค์


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่าย (สตางค์, int) คำนวณด้วยจำนวนเต็มล้วน ปัดครึ่งขึ้นครั้งเดียวตอนท้าย"""
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if not isinstance(member, bool):
        raise ValueError("member must be a bool")
    subtotal = 0
    for i, it in enumerate(items):
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise ValueError(f"item {i}: must be a dict with price and qty")
        p, q = it["price"], it["qty"]
        if not _is_int(p) or p < 0:
            raise ValueError(f"item {i}: price must be a non-negative integer")
        if not _is_int(q) or q < 1:
            raise ValueError(f"item {i}: qty must be an integer >= 1")
        subtotal += p * q

    num = subtotal * 107
    den = 100
    if subtotal >= THRESHOLD:
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    return (2 * num + den) // (2 * den)  # half-up


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        total = cafe_bill(data.get("items"), data.get("member", False))
    except (ValueError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)
    print(json.dumps({"total": total}))


if __name__ == "__main__":
    main()
