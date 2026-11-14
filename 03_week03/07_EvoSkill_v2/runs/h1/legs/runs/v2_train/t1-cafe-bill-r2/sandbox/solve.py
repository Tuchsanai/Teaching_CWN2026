"""BaanKafe cafe bill calculator.

กติกา (หน่วยเป็นสตางค์ทั้งหมด):
- items: list ของ {"price": ราคาต่อชิ้น (int สตางค์, >= 0), "qty": จำนวนชิ้น (int >= 1)}
- ยอดรวม (subtotal) = sum(price * qty)
- ยอดรวมตั้งแต่ 500 บาท (50000 สตางค์) ขึ้นไป ลด 5%
- member = True ลดอีก 10% (คำนวณต่อจากยอดหลังลด 5%)
- บวก VAT 7% เป็นขั้นสุดท้าย
- ปัดครั้งเดียวตอนท้ายสุดด้วยการปัดครึ่งขึ้น ให้ได้จำนวนเต็มสตางค์
- คำนวณทั้งหมดด้วย Fraction เพื่อไม่ให้ float คลาดเคลื่อน
"""

import json
import sys
from fractions import Fraction
from math import floor

DISCOUNT_THRESHOLD = 50000  # 500 บาท เป็นสตางค์
DISCOUNT_RATE = Fraction(5, 100)
MEMBER_RATE = Fraction(10, 100)
VAT_RATE = Fraction(7, 100)


def _half_up(x):
    """ปัดครึ่งขึ้น สำหรับ x >= 0: 2.5 -> 3, 2.4 -> 2."""
    return floor(Fraction(x) + Fraction(1, 2))


def _validate_items(items):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    for i, item in enumerate(items):
        if type(item) is not dict:
            raise ValueError(f"items[{i}] ต้องเป็น dict")
        if "price" not in item or "qty" not in item:
            raise ValueError(f"items[{i}] ต้องมี key 'price' และ 'qty'")
        price = item["price"]
        qty = item["qty"]
        if type(price) is not int:
            raise ValueError(f"items[{i}].price ต้องเป็น int (สตางค์)")
        if type(qty) is not int:
            raise ValueError(f"items[{i}].qty ต้องเป็น int")
        if price < 0:
            raise ValueError(f"items[{i}].price ต้องไม่ติดลบ")
        if qty < 1:
            raise ValueError(f"items[{i}].qty ต้องมีค่าตั้งแต่ 1")


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์."""
    _validate_items(items)
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น bool")

    subtotal = sum(item["price"] * item["qty"] for item in items)

    total = Fraction(subtotal)
    if subtotal >= DISCOUNT_THRESHOLD:
        total *= 1 - DISCOUNT_RATE
    if member:
        total *= 1 - MEMBER_RATE
    total *= 1 + VAT_RATE

    return _half_up(total)


def main():
    try:
        raw = sys.stdin.read()
        args = json.loads(raw)
        if type(args) is not dict:
            raise ValueError("input ต้องเป็น JSON object")
        result = cafe_bill(**args)
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
