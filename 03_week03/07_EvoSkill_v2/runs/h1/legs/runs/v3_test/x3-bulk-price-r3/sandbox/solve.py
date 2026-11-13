"""BaanKafe: คิดราคาขายส่งเมล็ดกาแฟ"""

import json
import sys
from fractions import Fraction


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def _require_int(value, label, lo=None, hi=None):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and value > hi:
        raise ValueError(f"{label} ต้องไม่เกิน {hi}")
    return value


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    - unit_price: ราคาต่อถุง (สตางค์, int, >= 0)
    - qty: จำนวนถุง (int, 1..1000)
    - coupon: True ถ้ามีคูปอง
    ลำดับการคิด: ส่วนลดตามจำนวน (ใช้อัตราเดียว) -> คูปองลดอีก 2.5% -> VAT 7%
    คูณทุกขั้นเป็น Fraction แล้วปัดครึ่งขึ้นครั้งเดียวตอนท้าย
    """
    _require_int(unit_price, "unit_price", lo=0)
    _require_int(qty, "qty", lo=1, hi=1000)
    if type(coupon) is not bool:
        raise ValueError("coupon ต้องเป็น True หรือ False")

    if qty >= 50:
        discount = Fraction(75, 1000)   # 7.5%
    elif qty >= 10:
        discount = Fraction(35, 1000)   # 3.5%
    else:
        discount = Fraction(0)

    amount = Fraction(unit_price * qty)
    amount *= 1 - discount
    if coupon:
        amount *= Fraction(975, 1000)   # ลดอีก 2.5%
    amount *= Fraction(107, 100)        # VAT 7% เป็นขั้นสุดท้าย
    return _half_up(amount)


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
