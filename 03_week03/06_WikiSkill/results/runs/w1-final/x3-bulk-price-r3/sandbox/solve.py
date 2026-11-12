import json
import sys


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
    _int(unit_price, 'unit_price', 0)
    _int(qty, 'qty', 1, 1000)
    _bool(coupon, 'coupon')
    num = unit_price * qty
    den = 1
    if qty >= 50:
        num, den = num * 925, den * 1000
    elif qty >= 10:
        num, den = num * 965, den * 1000
    if coupon:
        num, den = num * 975, den * 1000
    num, den = num * 107, den * 100  # VAT 7% ขั้นสุดท้าย
    return (2 * num + den) // (2 * den)  # half-up ปัดครั้งเดียว


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
