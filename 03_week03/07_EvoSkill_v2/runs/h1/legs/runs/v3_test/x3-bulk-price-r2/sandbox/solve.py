"""BaanKafe: คิดราคาขายส่งเมล็ดกาแฟ

กติกา (ทำตามลำดับนี้):
1. ยอดตั้งต้น = unit_price * qty (สตางค์)
2. ส่วนลดขายส่งตามจำนวนถุง อัตราเดียว: 50 ถุงขึ้นไป 7.5%, 10 ถุงขึ้นไป 3.5%
3. ถ้ามีคูปอง ลดอีก 2.5% (คูณต่อจากข้อ 2)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. ปัดครึ่งขึ้นเป็นสตางค์จำนวนเต็ม ครั้งเดียวตอนท้าย
"""

import json
import sys
from fractions import Fraction

VAT_RATE = Fraction(7, 100)
COUPON_RATE = Fraction(25, 1000)  # 2.5%


def _require_int(value, label, lo=None, hi=None):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and value > hi:
        raise ValueError(f"{label} ต้องไม่เกิน {hi}")
    return value


def _bulk_rate(qty):
    if qty >= 50:
        return Fraction(75, 1000)  # 7.5%
    if qty >= 10:
        return Fraction(35, 1000)  # 3.5%
    return Fraction(0)


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม รับ int หรือ Fraction ที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    unit_price: ราคาต่อถุง (สตางค์, int >= 0)
    qty: จำนวนถุง (int 1..1000)
    coupon: True ถ้ามีคูปอง
    """
    unit_price = _require_int(unit_price, "unit_price", lo=0)
    qty = _require_int(qty, "qty", lo=1, hi=1000)
    if type(coupon) is not bool:
        raise ValueError("coupon ต้องเป็น True หรือ False")

    amount = Fraction(unit_price * qty)
    amount *= 1 - _bulk_rate(qty)
    if coupon:
        amount *= 1 - COUPON_RATE
    amount *= 1 + VAT_RATE
    return half_up(amount)


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
