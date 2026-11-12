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


def refund(paid, used_percent, restock):
    _int(paid, 'paid', 0)
    _int(used_percent, 'used_percent', 0, 100)
    _bool(restock, 'restock')
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7  # หัก 12.5% => เหลือ 7/8
        den *= 8
    return (2 * num + den) // (2 * den)  # half-up ครั้งเดียวตอนท้าย


def main():
    try:
        data = json.loads(sys.stdin.read())
        result = refund(data['paid'], data['used_percent'], data['restock'])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}))
        return 2
    print(json.dumps({'ok': True, 'result': result}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
