import json
import sys


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่าย (int สตางค์) ปัดเศษครั้งเดียวตอนท้าย ปัดครึ่งขึ้น"""
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if not isinstance(member, bool):
        raise ValueError("member must be a bool")
    total = 0
    for it in items:
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise ValueError("each item needs price and qty")
        p, q = it["price"], it["qty"]
        if not _is_int(p) or not _is_int(q):
            raise ValueError("price and qty must be int")
        if p < 0 or q < 1:
            raise ValueError("price must be >= 0 and qty >= 1")
        total += p * q

    num, den = total, 1
    if total >= 50000:  # 500 บาท
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be an object")
        out = {"total": cafe_bill(data.get("items"), data.get("member", False))}
    except (ValueError, TypeError) as e:
        print(json.dumps({"error": str(e)}))
        return 1
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
