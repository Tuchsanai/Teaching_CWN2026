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


def shipping_fee(weight_g, distance_km, express):
    w = _int(weight_g, 'weight_g', 1, 30000)
    d = _int(distance_km, 'distance_km', 0)
    e = _bool(express, 'express')
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction((w - 5000) * 1500, 1000)
    if d > 100:
        fee *= Fraction(120, 100)
    if e:
        fee *= Fraction(150, 100)
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)


def main():
    try:
        data = json.loads(sys.stdin.read())
        result = shipping_fee(data['weight_g'], data['distance_km'], data['express'])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}))
        return 2
    print(json.dumps({'ok': True, 'result': result}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
