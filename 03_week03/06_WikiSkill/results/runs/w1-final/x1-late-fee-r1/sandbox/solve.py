import json
import sys
from fractions import Fraction


def _int(x, name, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f'{name} must be int')
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f'{name} out of range')
    return x


def late_fee(amount, days_late):
    _int(amount, 'amount', 0)
    _int(days_late, 'days_late', 0, 365)
    if days_late <= 3:
        return 0
    fee = Fraction(amount * 75 * days_late, 10000)
    cap = Fraction(amount * 15, 100)
    fee = min(fee, cap)
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)


def main():
    try:
        data = json.loads(sys.stdin.read())
        result = late_fee(data['amount'], data['days_late'])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}))
        return 2
    print(json.dumps({'ok': True, 'result': result}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
