import sys
import json
from fractions import Fraction


def _half_up(x: Fraction) -> int:
    n, d = x.numerator, x.denominator
    return (2 * n + d) // (2 * d)


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


def bulk_price(unit_price, qty, coupon):
    unit_price = _int(unit_price, "unit_price", lo=0)
    qty = _int(qty, "qty", lo=1, hi=1000)
    coupon = _bool(coupon, "coupon")

    # อัตราส่วนลดขายส่ง (อัตราเดียว): >=50 ถุง ลด 7.5%, >=10 ถุง ลด 3.5%
    if qty >= 50:
        bulk = Fraction(75, 1000)
    elif qty >= 10:
        bulk = Fraction(35, 1000)
    else:
        bulk = Fraction(0)

    # ตัวคูณทั้งหมดรวมเป็นเศษส่วนก่อน ปัดเศษครั้งเดียวตอนท้าย
    factor = (1 - bulk)
    if coupon:
        factor *= (1 - Fraction(25, 1000))  # ลดอีก 2.5% (ลดต่อจากราคาหลังขายส่ง)
    factor *= (1 + Fraction(7, 100))        # VAT 7% เป็นขั้นสุดท้าย

    total = Fraction(unit_price * qty) * factor
    return _half_up(total)


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
