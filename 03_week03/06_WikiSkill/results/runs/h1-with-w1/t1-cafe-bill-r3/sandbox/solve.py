import json
import sys
from fractions import Fraction

# หน่วยเงินทั้งหมดเป็นสตางค์ (จำนวนเต็ม)
DISCOUNT_THRESHOLD = 50000          # 500 บาท
DISCOUNT_RATE = Fraction(5, 100)    # ลด 5% เมื่อยอดรวมถึงเกณฑ์
MEMBER_RATE = Fraction(10, 100)     # สมาชิกลดอีก 10%
VAT_RATE = Fraction(7, 100)         # VAT 7% ขั้นสุดท้าย


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


def _round_half_up(frac):
    # ใช้กับค่าที่ไม่ติดลบเท่านั้น
    return (2 * frac.numerator + frac.denominator) // (2 * frac.denominator)


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นสตางค์ (จำนวนเต็ม)

    items: list ของ {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก
    """
    if not isinstance(items, list):
        raise ValueError('items must be list')
    if len(items) == 0:
        raise ValueError('items must not be empty')

    subtotal = 0
    for item in items:
        if not isinstance(item, dict):
            raise ValueError('each item must be dict')
        if 'price' not in item or 'qty' not in item:
            raise ValueError('each item must have price and qty')
        price = _int(item['price'], 'price', lo=1)
        qty = _int(item['qty'], 'qty', lo=1)
        subtotal += price * qty

    member = _bool(member, 'member')

    # คูณอัตราทั้งหมดด้วย Fraction ไม่ปัดกลางทาง
    rate = Fraction(1)
    if subtotal >= DISCOUNT_THRESHOLD:
        rate *= 1 - DISCOUNT_RATE
    if member:
        rate *= 1 - MEMBER_RATE

    total = Fraction(subtotal) * rate * (1 + VAT_RATE)
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
