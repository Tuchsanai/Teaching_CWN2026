import json
import sys


def _check_int(v, name, minimum):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be int")
    if v < minimum:
        raise ValueError(f"{name} must be >= {minimum}")


def cafe_bill(items, member):
    """คืนยอดสุทธิเป็นสตางค์ (int) ปัดเศษครั้งเดียวตอนท้าย ปัดครึ่งขึ้น"""
    if not isinstance(items, list):
        raise ValueError("items must be list")
    if not isinstance(member, bool):
        raise ValueError("member must be bool")
    total = 0
    for it in items:
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise ValueError("item must be dict with price and qty")
        _check_int(it["price"], "price", 0)
        _check_int(it["qty"], "qty", 1)
        total += it["price"] * it["qty"]

    num, den = total, 1
    if total >= 50000:          # 500 บาท
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100   # VAT 7% ขั้นสุดท้าย
    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น (ค่าไม่ติดลบ)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be object")
        result = {"total": cafe_bill(data.get("items"), data.get("member", False))}
        print(json.dumps(result))
    except (ValueError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
