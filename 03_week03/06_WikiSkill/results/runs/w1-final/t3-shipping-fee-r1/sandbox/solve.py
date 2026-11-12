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


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee in integer satang (half-up, rounded once)."""
    w = _int(weight_g, 'weight_g', 1, 30000)
    d = _int(distance_km, 'distance_km', 0)
    e = _bool(express, 'express')
    # base in satang as fraction num/den
    if w <= 1000:
        num, den = 4000, 1
    elif w <= 5000:
        num, den = 8000, 1
    else:
        # 80 baht + (w-5000)/1000 kg * 15 baht, in satang
        num, den = 8000 * 10 + 15 * (w - 5000), 10
    if d > 100:
        num, den = num * 6, den * 5
    if e:
        num, den = num * 3, den * 2
    return (2 * num + den) // (2 * den)


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
