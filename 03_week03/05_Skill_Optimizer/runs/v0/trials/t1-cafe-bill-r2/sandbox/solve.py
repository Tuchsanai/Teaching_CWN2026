import json
import sys


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่ายเป็นจำนวนเต็มสตางค์ (คำนวณด้วยจำนวนเต็มล้วน ปัดครึ่งขึ้นครั้งเดียวตอนท้าย)"""
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if not isinstance(member, bool):
        raise ValueError("member must be a bool")
    total = 0
    for i, it in enumerate(items):
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise ValueError(f"item {i}: must be dict with price and qty")
        price, qty = it["price"], it["qty"]
        if not _is_int(price) or price < 0:
            raise ValueError(f"item {i}: price must be a non-negative integer (satang)")
        if not _is_int(qty) or qty < 1:
            raise ValueError(f"item {i}: qty must be an integer >= 1")
        total += price * qty

    num, den = total, 1
    if total >= 50000:      # 500 บาท
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100   # VAT 7%
    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(data.get("items"), data.get("member", False))
        print(json.dumps({"total": result}))
    except (ValueError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
