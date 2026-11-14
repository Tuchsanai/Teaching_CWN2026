"""BaanKafe cashier bill calculator.

กติกา (ตามโจทย์):
1. ยอดรวมก่อนลด = sum(price * qty) หน่วยสตางค์
2. ถ้ายอดรวมก่อนลด >= 50000 สตางค์ (500 บาท) ลด 5%
3. ถ้า member = True ลดอีก 10% (คิดต่อจากยอดหลังข้อ 2)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. ปัดครั้งเดียวตอนท้ายสุด ปัดครึ่งขึ้น ได้จำนวนเต็มสตางค์

การตีความที่เลือกเอง:
- เกณฑ์ 500 บาท ใช้ยอดก่อนลด 5%
- "ลดอีก 10%" คิดทบต่อจากยอดหลังลด 5% (ไม่ใช่บวกรวมเป็น 15%)
- items ว่าง คืน 0
- price เป็นจำนวนเต็มสตางค์ >= 0, qty เป็นจำนวนเต็ม >= 1
"""

import json
import sys
from fractions import Fraction
from math import floor

THRESHOLD_SATANG = 50000  # 500 บาท
THRESHOLD_DISCOUNT = Fraction(5, 100)
MEMBER_DISCOUNT = Fraction(10, 100)
VAT_RATE = Fraction(7, 100)


def _half_up(x):
    # ปัดครึ่งขึ้น สำหรับ x >= 0: 2.4 -> 2, 2.5 -> 3
    return floor(Fraction(x) + Fraction(1, 2))


def _validate_item(item):
    if type(item) is not dict:
        raise ValueError("each item must be a dict")
    if "price" not in item or "qty" not in item:
        raise ValueError("each item must have 'price' and 'qty'")
    price = item["price"]
    qty = item["qty"]
    if type(price) is not int:
        raise ValueError("price must be an int (satang)")
    if type(qty) is not int:
        raise ValueError("qty must be an int")
    if price < 0:
        raise ValueError("price must be >= 0")
    if qty < 1:
        raise ValueError("qty must be >= 1")
    return price, qty


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"""
    try:
        if type(items) is not list:
            raise ValueError("items must be a list")
        if type(member) is not bool:
            raise ValueError("member must be a bool")

        subtotal = 0
        for item in items:
            price, qty = _validate_item(item)
            subtotal += price * qty

        total = Fraction(subtotal)
        if subtotal >= THRESHOLD_SATANG:
            total *= 1 - THRESHOLD_DISCOUNT
        if member:
            total *= 1 - MEMBER_DISCOUNT
        total *= 1 + VAT_RATE

        return _half_up(total)
    except ValueError:
        raise
    except (TypeError, KeyError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError(str(exc)) from exc


def main():
    try:
        args = json.loads(sys.stdin.read())
        if type(args) is not dict:
            raise ValueError("input must be a JSON object")
        result = cafe_bill(**args)
    except (ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
