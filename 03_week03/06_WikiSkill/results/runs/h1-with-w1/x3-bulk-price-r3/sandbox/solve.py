"""BaanKafe bulk coffee-bean pricing.

หน่วยเงินเป็นสตางค์ (จำนวนเต็ม) คำนวณด้วย Fraction แล้วปัดครั้งเดียวตอนท้ายแบบ half-up

กติกา:
- ซื้อ >= 50 ถุง ลด 7.5%, ซื้อ >= 10 ถุง ลด 3.5% (ใช้อัตราเดียวตามจำนวนถุง)
- มีคูปอง ลดอีก 2.5% (คิดต่อจากราคาหลังลดขายส่ง)
- บวก VAT 7% เป็นขั้นสุดท้าย
"""

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


def _bulk_rate(qty):
    if qty >= 50:
        return Fraction(75, 1000)
    if qty >= 10:
        return Fraction(35, 1000)
    return Fraction(0)


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นสตางค์ (จำนวนเต็ม) หลังลดและบวก VAT"""
    unit_price = _int(unit_price, 'unit_price', lo=0)
    qty = _int(qty, 'qty', lo=1, hi=1000)
    coupon = _bool(coupon, 'coupon')

    total = Fraction(unit_price * qty)
    total *= 1 - _bulk_rate(qty)
    if coupon:
        total *= 1 - Fraction(25, 1000)
    total *= 1 + Fraction(7, 100)

    num, den = total.numerator, total.denominator
    return (2 * num + den) // (2 * den)  # half-up, ปัดครั้งเดียว (num/den >= 0 เสมอ)


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
