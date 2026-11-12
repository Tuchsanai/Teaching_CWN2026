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


def _round_half_up(q):
    # q: Fraction >= 0 -> จำนวนเต็มที่ใกล้สุด, .5 ปัดขึ้น
    num, den = q.numerator, q.denominator
    return (2 * num + den) // (2 * den)


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นสตางค์ (จำนวนเต็ม)

    items: list ของ {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ลดเพิ่มอีก 10%
    กฎ: รวม >= 50,000 สตางค์ (500 บาท) ลด 5% -> member ลด 10% -> VAT 7%
    """
    if not isinstance(items, list) or not items:
        raise ValueError('items must be a non-empty list')

    subtotal = 0
    for it in items:
        if not isinstance(it, dict) or 'price' not in it or 'qty' not in it:
            raise ValueError('each item must be a dict with price and qty')
        price = _int(it['price'], 'price', lo=1)
        qty = _int(it['qty'], 'qty', lo=1)
        subtotal += price * qty

    member = _bool(member, 'member')

    total = Fraction(subtotal)
    if subtotal >= 50000:  # 500 บาท = 50,000 สตางค์
        total *= Fraction(95, 100)
    if member:
        total *= Fraction(90, 100)
    total *= Fraction(107, 100)  # VAT 7% เป็นขั้นสุดท้าย

    return _round_half_up(total)


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
