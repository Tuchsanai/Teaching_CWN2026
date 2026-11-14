"""BaanKafe: คิดเงินหน้าร้าน

กติกา
1. ยอดรวมก่อนลด = sum(price * qty) หน่วยสตางค์
2. ยอดรวมตั้งแต่ 500 บาท (50000 สตางค์) ขึ้นไป ลด 5%
3. ถ้า member = True ลดอีก 10% (คิดต่อจากยอดหลังลด 5%)
4. บวก VAT 7% เป็นขั้นสุดท้าย (คิดจากยอดหลังลดทั้งหมด)
5. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ครั้งเดียวตอนท้ายสุด

หมายเหตุการตีความ
- เกณฑ์ 500 บาทใช้ยอดรวมก่อนลดทั้งหมด (ก่อนหักส่วนลดสมาชิก)
- ส่วนลดสมาชิกคิดต่อจากยอดหลังลด 5% (ทบต้น) ไม่ได้รวมกับ 5% เป็น 15%
"""

import json
import sys
from fractions import Fraction
from math import floor

THRESHOLD_SATANG = 50000  # 500 บาท
ITEM_KEYS = {"price", "qty"}


def _half_up(x):
    # ปัดครึ่งขึ้น สำหรับ x >= 0: 2.4 -> 2, 2.5 -> 3
    return floor(Fraction(x) + Fraction(1, 2))


def _validate_items(items):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    for i, item in enumerate(items):
        if type(item) is not dict:
            raise ValueError(f"items[{i}] ต้องเป็น dict")
        if set(item.keys()) != ITEM_KEYS:
            raise ValueError(f"items[{i}] ต้องมีเฉพาะ key 'price' และ 'qty'")
        price = item["price"]
        qty = item["qty"]
        if type(price) is not int or price < 0:
            raise ValueError(f"items[{i}].price ต้องเป็น int >= 0 (สตางค์)")
        if type(qty) is not int or qty < 1:
            raise ValueError(f"items[{i}].qty ต้องเป็น int >= 1")


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"""
    _validate_items(items)
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น bool")

    try:
        subtotal = sum(item["price"] * item["qty"] for item in items)  # int สตางค์

        # ส่วนลดตามยอดรวม: ตั้งแต่ 500 บาทขึ้นไป ลด 5%
        total = Fraction(subtotal)
        if subtotal >= THRESHOLD_SATANG:
            total *= Fraction(95, 100)

        # ส่วนลดสมาชิก: ลดอีก 10% ทบจากยอดที่ลดแล้ว
        if member:
            total *= Fraction(90, 100)

        # VAT 7% ขั้นสุดท้าย แล้วปัดครั้งเดียว
        total *= Fraction(107, 100)
        return _half_up(total)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError(f"คำนวณไม่ได้: {exc}") from exc


def main():
    try:
        args = json.load(sys.stdin)
        if type(args) is not dict:
            raise ValueError("stdin ต้องเป็น JSON object")
        result = cafe_bill(**args)
    except (ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
