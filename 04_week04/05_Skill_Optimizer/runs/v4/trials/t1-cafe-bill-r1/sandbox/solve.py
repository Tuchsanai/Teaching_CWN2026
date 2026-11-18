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
        if not isinstance(it, dict):
            raise ValueError("item must be a dict")
        price, qty = it.get("price"), it.get("qty")
        if not _is_int(price) or price < 0:
            raise ValueError("price must be a non-negative int")
        if not _is_int(qty) or qty < 1:
            raise ValueError("qty must be an int >= 1")
        total += price * qty

    num, den = total * 107, 100  # VAT 7%
    if total >= 50000:  # 500 บาท
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น


def main():
    data = json.load(sys.stdin)
    try:
        out = {"total": cafe_bill(data.get("items"), data.get("member"))}
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
