"""
BaanKafe: คิดราคาขายส่งเมล็ดกาแฟ

กติกา (ตามโจทย์):
1. unit_price = ราคาต่อถุง หน่วยสตางค์ จำนวนเต็ม >= 0
2. qty = จำนวนถุง จำนวนเต็ม 1..1000
3. coupon = True คือมีคูปอง (ต้องเป็น bool)
4. ซื้อ >= 50 ถุง ลด 7.5%, ซื้อ >= 10 ถุง ลด 3.5% (ใช้อัตราเดียว ไม่สะสม)
5. มีคูปอง ลดอีก 2.5% คิดจากยอดหลังข้อ 4 (ทบต้น)
6. บวก VAT 7% เป็นขั้นสุดท้าย
7. คำนวณด้วย Fraction ปัดครึ่งขึ้นครั้งเดียวตอนท้าย คืนจำนวนเต็มสตางค์
"""

import json
import sys
from fractions import Fraction
from math import floor


def bulk_price(unit_price, qty, coupon):
    # ตรวจชนิดแบบเข้มงวด: bool เป็น subclass ของ int จึงใช้ type(x) is int
    if type(unit_price) is not int:
        raise ValueError("unit_price ต้องเป็นจำนวนเต็มหน่วยสตางค์")
    if unit_price < 0:
        raise ValueError("unit_price ต้องไม่ติดลบ")

    if type(qty) is not int:
        raise ValueError("qty ต้องเป็นจำนวนเต็ม")
    if not (1 <= qty <= 1000):
        raise ValueError("qty ต้องอยู่ระหว่าง 1 ถึง 1000")

    if type(coupon) is not bool:
        raise ValueError("coupon ต้องเป็น true หรือ false")

    # ส่วนลดตามจำนวน (อัตราเดียว ไม่สะสม)
    if qty >= 50:
        bulk_rate = Fraction(75, 1000)  # 7.5%
    elif qty >= 10:
        bulk_rate = Fraction(35, 1000)  # 3.5%
    else:
        bulk_rate = Fraction(0)

    total = Fraction(unit_price * qty) * (1 - bulk_rate)

    # คูปองลดอีก 2.5% จากยอดที่ลดแล้ว
    if coupon:
        total *= 1 - Fraction(25, 1000)

    # VAT 7% เป็นขั้นสุดท้าย
    total *= Fraction(107, 100)

    # ปัดครึ่งขึ้นครั้งเดียว
    return floor(total + Fraction(1, 2))


def main():
    try:
        args = json.loads(sys.stdin.read())
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = bulk_price(**args)
    except (ValueError, TypeError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
