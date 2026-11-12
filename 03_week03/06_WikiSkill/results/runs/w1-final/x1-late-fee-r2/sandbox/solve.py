import json
import sys


def _int(x, name, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f'{name} must be int')
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f'{name} out of range')
    return x


def late_fee(amount, days_late):
    _int(amount, 'amount', lo=0)
    _int(days_late, 'days_late', lo=0, hi=365)
    if days_late <= 3:
        return 0
    # rate in basis points: 0.75%/day = 75 bp, capped at 15% = 1500 bp
    bp = min(75 * days_late, 1500)
    num, den = amount * bp, 10000
    return (2 * num + den) // (2 * den)


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
