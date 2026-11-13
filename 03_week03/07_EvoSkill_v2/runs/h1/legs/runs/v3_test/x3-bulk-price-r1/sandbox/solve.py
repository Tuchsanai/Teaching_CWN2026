"""BaanKafe: คิดราคาขายส่งเมล็ดกาแฟ

กติกา (ตามสเปก):
- unit_price: ราคาต่อถุง หน่วยสตางค์ จำนวนเต็ม ตั้งแต่ 0
- qty: จำนวนถุง จำนวนเต็ม 1–1000
- coupon: True ถ้ามีคูปอง
- ซื้อ 10 ถุงขึ้นไป ลด 3.5%, ซื้อ 50 ถุงขึ้นไป ลด 7.5% (ใช้อัตราเดียว ไม่บวกซ้อน)
- มีคูปอง ลดอีก 2.5% (คูณต่อจากส่วนลดข้อแรก)
- บวก VAT 7% เป็นขั้นสุดท้าย
- คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์ ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
"""

import json
import sys
from fractions import Fraction


def _require_int(value, label, lo, hi=None):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and value > hi:
        raise ValueError(f"{label} ต้องไม่เกิน {hi}")
    return value


def _require_flag(value, label):
    if type(value) is not bool:
        raise ValueError(f"{label} ต้องเป็น True หรือ False")
    return value


def _bulk_rate(qty):
    """อัตราส่วนลดตามจำนวนถุง (ไม่ซ้อนกัน): >=50 ได้ 7.5%, >=10 ได้ 3.5%"""
    if qty >= 50:
        return Fraction(75, 1000)
    if qty >= 10:
        return Fraction(35, 1000)
    return Fraction(0)


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์"""
    unit_price = _require_int(unit_price, "unit_price", 0)
    qty = _require_int(qty, "qty", 1, 1000)
    coupon = _require_flag(coupon, "coupon")

    amount = Fraction(unit_price * qty)                 # ยอดก่อนลด (สตางค์)
    amount *= 1 - _bulk_rate(qty)                       # ส่วนลดตามจำนวน
    if coupon:
        amount *= 1 - Fraction(25, 1000)                # คูปองลดอีก 2.5%
    amount *= 1 + Fraction(7, 100)                      # VAT 7% เป็นขั้นสุดท้าย

    # ปัดครึ่งขึ้นครั้งเดียว (amount ไม่ติดลบเสมอ)
    return int((amount * 2 + 1) // 2)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = bulk_price(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
