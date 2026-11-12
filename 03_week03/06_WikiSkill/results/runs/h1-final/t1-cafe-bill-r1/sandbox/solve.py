import sys
import json
from fractions import Fraction

# เกณฑ์ลด 5%: ยอดรวม 500 บาท = 50,000 สตางค์
DISCOUNT_THRESHOLD = 50000


def _half_up(x: Fraction) -> int:
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def _int(v, name, lo=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be an integer")
    if lo is not None and v < lo:
        raise ValueError(f"{name} out of range")
    return v


def _bool(v, name):
    if not isinstance(v, bool):
        raise ValueError(f"{name} must be a bool")
    return v


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ลดเพิ่มอีก 10%
    ลำดับ: ยอดรวม -> ลด 5% (ถ้าถึงเกณฑ์) -> ลด 10% (ถ้าเป็นสมาชิก) -> VAT 7%
    ปัดเศษแบบ half up ครั้งเดียวตอนท้าย
    """
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    member = _bool(member, "member")

    subtotal = 0
    for i, item in enumerate(items):
        if not isinstance(item, dict) or "price" not in item or "qty" not in item:
            raise ValueError(f"items[{i}] must be a dict with price and qty")
        price = _int(item["price"], f"items[{i}].price", lo=0)
        qty = _int(item["qty"], f"items[{i}].qty", lo=1)
        subtotal += price * qty

    total = Fraction(subtotal)
    if subtotal >= DISCOUNT_THRESHOLD:
        total *= Fraction(95, 100)
    if member:
        total *= Fraction(90, 100)
    total *= Fraction(107, 100)
    return _half_up(total)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(**data)
        out = json.dumps({"ok": True, "result": result})
    except Exception as e:  # รวม JSON เสีย, key เกิน/ขาด, ValueError
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
