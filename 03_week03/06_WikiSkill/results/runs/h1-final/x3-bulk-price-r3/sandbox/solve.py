"""คิดราคาขายส่งเมล็ดกาแฟ BaanKafe (หน่วยเป็นสตางค์)

กติกา:
- ซื้อ 10 ถุงขึ้นไป ลด 3.5%, ซื้อ 50 ถุงขึ้นไป ลด 7.5% (ใช้อัตราเดียว ไม่สะสม)
- มีคูปอง ลดอีก 2.5% (ลดต่อจากส่วนลดปริมาณ)
- บวก VAT 7% เป็นขั้นสุดท้าย
- ปัดเศษแบบ half up ครั้งเดียวตอนท้าย คืนจำนวนเต็มสตางค์
"""
import json
import sys
from fractions import Fraction


def _int(v, name, lo=None, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be an integer")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def _bool(v, name):
    if not isinstance(v, bool):
        raise ValueError(f"{name} must be a bool")
    return v


def _half_up(x: Fraction) -> int:
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def bulk_price(unit_price, qty, coupon):
    unit_price = _int(unit_price, "unit_price", lo=0)
    qty = _int(qty, "qty", lo=1, hi=1000)
    coupon = _bool(coupon, "coupon")

    if qty >= 50:
        discount = Fraction(75, 1000)
    elif qty >= 10:
        discount = Fraction(35, 1000)
    else:
        discount = Fraction(0)

    factor = (1 - discount) * Fraction(107, 100)  # ส่วนลดปริมาณ, then VAT 7%
    if coupon:
        factor *= 1 - Fraction(25, 1000)           # คูปองลดอีก 2.5%

    return _half_up(unit_price * qty * factor)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = bulk_price(**data)
        out = json.dumps({"ok": True, "result": result})
    except Exception as e:  # รวม JSON เสีย, key เกิน/ขาด, ValueError
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
