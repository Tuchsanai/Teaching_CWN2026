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


def cafe_bill(items, member):
    if not isinstance(items, list):
        raise ValueError('items must be list')
    if not items:
        raise ValueError('items must not be empty')
    _bool(member, 'member')
    total = 0
    for it in items:
        if not isinstance(it, dict):
            raise ValueError('item must be dict')
        if 'price' not in it or 'qty' not in it:
            raise ValueError('item needs price and qty')
        price = _int(it['price'], 'price', 0)
        qty = _int(it['qty'], 'qty', 1)
        total += price * qty
    num, den = total, 1
    if total >= 50000:
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError('input must be object')
        result = cafe_bill(data['items'], data['member'])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}))
        return 2
    print(json.dumps({'ok': True, 'result': result}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
