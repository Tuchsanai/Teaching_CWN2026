#!/usr/bin/env python3
"""BaanKafe: cafe_bill(items, member)

กติกา
1. subtotal = sum(price * qty) เป็นสตางค์ (จำนวนเต็ม)
2. ถ้า subtotal >= 50000 สตางค์ (500 บาท) ลด 5%
3. ถ้า member เป็น True ลดอีก 10% (คิดต่อจากยอดหลังลด 5%)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. คำนวณทั้งหมดด้วย Fraction แล้วปัดครึ่งขึ้นครั้งเดียวตอนท้ายสุด
"""
import json
import sys
from fractions import Fraction
from math import floor

THRESHOLD_SATANG = 50000  # 500 บาท


def _half_up(x):
    # ปัดครึ่งขึ้น สำหรับ x >= 0: 53.5 -> 54, 53.4 -> 53
    return floor(Fraction(x) + Fraction(1, 2))


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น bool")

    subtotal = 0
    for item in items:
        if type(item) is not dict:
            raise ValueError("แต่ละรายการใน items ต้องเป็น dict")
        if "price" not in item or "qty" not in item:
            raise ValueError("แต่ละรายการต้องมี key price และ qty")
        price = item["price"]
        qty = item["qty"]
        if type(price) is not int or price < 0:
            raise ValueError("price ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
        if type(qty) is not int or qty < 1:
            raise ValueError("qty ต้องเป็นจำนวนเต็มตั้งแต่ 1 ขึ้นไป")
        subtotal += price * qty

    total = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:
        total *= Fraction(95, 100)
    if member:
        total *= Fraction(90, 100)
    total *= Fraction(107, 100)

    return _half_up(total)


def main():
    try:
        args = json.loads(sys.stdin.read())
        if type(args) is not dict:
            raise ValueError("input ต้องเป็น JSON object")
        result = cafe_bill(**args)
    except (ValueError, TypeError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
