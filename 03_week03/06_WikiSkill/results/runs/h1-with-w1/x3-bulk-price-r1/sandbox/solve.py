"""BaanKafe bulk coffee-bean pricing.

หน่วยเป็นสตางค์ทั้งหมด (จำนวนเต็ม) ไม่ใช้ float
ลำดับการคิด: ยอดดิบ -> ส่วนลดจำนวนถุง (อัตราเดียว) -> คูปอง -> VAT 7% (ขั้นสุดท้าย)
ปัดเศษ half-up ครั้งเดียวตอนท้าย
"""
import json
import sys
from fractions import Fraction

# (จำนวนถุงขั้นต่ำ, อัตราส่วนลด) เรียงจากมากไปน้อย ใช้อัตราเดียวตามขั้นที่ถึง
BULK_TIERS = (
    (50, Fraction(75, 1000)),  # 7.5%
    (10, Fraction(35, 1000)),  # 3.5%
)
COUPON_RATE = Fraction(25, 1000)  # 2.5%
VAT_RATE = Fraction(7, 100)       # 7%


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


def _round_half_up(f):
    """ปัดเศษ half-up สำหรับค่าที่ไม่ติดลบ (ใช้จำนวนเต็มล้วน)"""
    num, den = f.numerator, f.denominator
    return (2 * num + den) // (2 * den)


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นสตางค์ (จำนวนเต็ม)

    unit_price: ราคาต่อถุง (สตางค์, ตั้งแต่ 0)
    qty: จำนวนถุง (1–1000)
    coupon: True ถ้ามีคูปอง
    """
    unit_price = _int(unit_price, 'unit_price', lo=0)
    qty = _int(qty, 'qty', lo=1, hi=1000)
    coupon = _bool(coupon, 'coupon')

    total = Fraction(unit_price * qty)

    for min_qty, rate in BULK_TIERS:
        if qty >= min_qty:
            total *= 1 - rate
            break

    if coupon:
        total *= 1 - COUPON_RATE

    total *= 1 + VAT_RATE

    return _round_half_up(total)


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
