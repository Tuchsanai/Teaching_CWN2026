import json
import sys
from fractions import Fraction


def _int(x, name, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f'{name} must be int')
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f'{name} out of range')
    return x


def _bool(x, name):
    if not isinstance(x, bool):
        raise ValueError(f'{name} must be bool')
    return x


def bulk_price(unit_price, qty, coupon):
    """ราคาที่ลูกค้าต้องจ่ายสำหรับเมล็ดกาแฟขายส่ง (หน่วยสตางค์ ปัดครึ่งขึ้น)

    - ซื้อ >= 50 ถุง ลด 7.5%, ซื้อ >= 10 ถุง ลด 3.5% (ใช้อัตราเดียว ไม่สะสม)
    - มีคูปอง ลดอีก 2.5% จากราคาหลังลดปริมาณ
    - บวก VAT 7% เป็นขั้นสุดท้าย
    """
    unit_price = _int(unit_price, 'unit_price', lo=0)
    qty = _int(qty, 'qty', lo=1, hi=1000)
    coupon = _bool(coupon, 'coupon')

    if qty >= 50:
        factor = 1 - Fraction(3, 40)    # ลด 7.5%
    elif qty >= 10:
        factor = 1 - Fraction(7, 200)   # ลด 3.5%
    else:
        factor = Fraction(1)

    if coupon:
        factor *= 1 - Fraction(1, 40)   # ลดอีก 2.5%

    total = Fraction(unit_price * qty) * factor * Fraction(107, 100)  # VAT 7%

    # ปัดครั้งเดียวตอนท้าย แบบครึ่งขึ้น (half-up)
    num, den = total.numerator, total.denominator
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        result = bulk_price(data['unit_price'], data['qty'], data['coupon'])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}))
        return 2
    print(json.dumps({'ok': True, 'result': result}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
