"""BaanKafe cafe bill calculator.

หน่วยเงินทั้งหมดเป็นสตางค์ (จำนวนเต็ม)

กติกา:
1. ยอดรวมก่อนลด = sum(price * qty)
2. ยอดรวมตั้งแต่ 500 บาท (50,000 สตางค์) ขึ้นไป ลด 5%
3. member = True ลดอีก 10%
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. ปัดเศษแบบ half-up ครั้งเดียวตอนท้าย คืนค่าเป็นจำนวนเต็มสตางค์
"""

import json
import sys
from fractions import Fraction

THRESHOLD_SATANG = 50_000  # 500 บาท
BULK_DISCOUNT = Fraction(95, 100)  # ลด 5%
MEMBER_DISCOUNT = Fraction(9, 10)  # ลด 10%
VAT = Fraction(107, 100)  # บวก VAT 7%


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


def _validate_items(items):
    if not isinstance(items, list):
        raise ValueError('items must be list')
    if len(items) == 0:
        raise ValueError('items must not be empty')
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f'items[{i}] must be dict')
        if 'price' not in item or 'qty' not in item:
            raise ValueError(f'items[{i}] must have price and qty')
        _int(item['price'], f'items[{i}].price', lo=1)
        _int(item['qty'], f'items[{i}].qty', lo=1)


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย (สตางค์, จำนวนเต็ม)"""
    _validate_items(items)
    _bool(member, 'member')

    subtotal = sum(item['price'] * item['qty'] for item in items)

    total = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:
        total *= BULK_DISCOUNT
    if member:
        total *= MEMBER_DISCOUNT
    total *= VAT

    # ปัด half-up ครั้งเดียวตอนท้าย (total >= 0 เสมอ)
    num, den = total.numerator, total.denominator
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        result = cafe_bill(data['items'], data['member'])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}))
        return 2
    print(json.dumps({'ok': True, 'result': result}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
