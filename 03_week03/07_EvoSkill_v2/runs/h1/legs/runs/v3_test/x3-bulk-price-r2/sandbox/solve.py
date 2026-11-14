"""BaanKafe: คิดราคาขายส่งเมล็ดกาแฟ

กติกา (หน่วยเป็นสตางค์ทั้งหมด):
- unit_price: ราคาต่อถุง เป็นจำนวนเต็มสตางค์ >= 0
- qty: จำนวนถุง เป็นจำนวนเต็ม 1..1000
- coupon: True = มีคูปอง, False = ไม่มี
- ซื้อ >= 50 ถุง ลด 7.5% (อัตราเดียว, แทนที่อัตรา 10 ถุง)
- ซื้อ >= 10 ถุง ลด 3.5%
- มีคูปอง ลดอีก 2.5% (คิดต่อจากยอดหลังลดขั้นแรก)
- บวก VAT 7% เป็นขั้นสุดท้าย
- ปัดครึ่งขึ้นครั้งเดียวที่ท้ายสุด คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์
"""

import json
import sys
from fractions import Fraction


def _half_up(x):
    # ปัดครึ่งขึ้น สำหรับ x >= 0: 2.4 -> 2, 2.5 -> 3
    return (Fraction(x) + Fraction(1, 2)).__floor__()


def _bulk_rate(qty):
    if qty >= 50:
        return Fraction(75, 1000)
    if qty >= 10:
        return Fraction(35, 1000)
    return Fraction(0)


def bulk_price(unit_price, qty, coupon):
    if type(unit_price) is not int:
        raise ValueError("unit_price ต้องเป็นจำนวนเต็ม (สตางค์)")
    if type(qty) is not int:
        raise ValueError("qty ต้องเป็นจำนวนเต็ม")
    if type(coupon) is not bool:
        raise ValueError("coupon ต้องเป็น true หรือ false")
    if unit_price < 0:
        raise ValueError("unit_price ต้องไม่ต่ำกว่า 0")
    if not (1 <= qty <= 1000):
        raise ValueError("qty ต้องอยู่ระหว่าง 1 ถึง 1000")

    total = Fraction(unit_price * qty)
    total *= 1 - _bulk_rate(qty)
    if coupon:
        total *= 1 - Fraction(25, 1000)
    total *= Fraction(107, 100)  # VAT 7% ขั้นสุดท้าย

    return _half_up(total)


def main():
    try:
        raw = sys.stdin.read()
        args = json.loads(raw)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = bulk_price(**args)
    except (ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
