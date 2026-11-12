import json
import sys

RATES = {"silver": (15, 1000), "gold": (25, 1000), "platinum": (4, 100)}
MIN_AMOUNT = 10000  # 100 baht in satang
CAP = 20000         # 200 baht in satang


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


def cashback(amount, tier, birthday):
    _int(amount, 'amount', lo=0)
    if not (isinstance(tier, str) and tier in RATES):
        raise ValueError('tier must be silver, gold or platinum')
    _bool(birthday, 'birthday')
    if amount < MIN_AMOUNT:
        return 0
    n, d = RATES[tier]
    num = amount * n * (2 if birthday else 1)
    den = d
    result = (2 * num + den) // (2 * den)  # half-up, rounded once
    return min(result, CAP)


def main():
    try:
        data = json.loads(sys.stdin.read())
        result = cashback(data['amount'], data['tier'], data['birthday'])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}))
        return 2
    print(json.dumps({'ok': True, 'result': result}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
