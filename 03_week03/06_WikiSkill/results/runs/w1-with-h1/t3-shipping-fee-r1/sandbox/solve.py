import sys
import json
from fractions import Fraction


def _half_up(x: Fraction) -> int:
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def _int(v, name, lo=None, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be an integer")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def _bool(v, name):
    if not isinstance(v, bool):
        raise ValueError(f"{name} must be a bool")
    return v


def shipping_fee(weight_g, distance_km, express):
    w = _int(weight_g, "weight_g", 1, 30000)
    d = _int(distance_km, "distance_km", 0)
    e = _bool(express, "express")
    if w <= 1000:
        baht = Fraction(40)
    elif w <= 5000:
        baht = Fraction(80)
    else:
        baht = 80 + Fraction((w - 5000) * 15, 1000)
    fee = baht * 100  # satang
    if d > 100:
        fee *= Fraction(120, 100)
    if e:
        fee *= Fraction(150, 100)
    return _half_up(fee)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = shipping_fee(**data)
        out = json.dumps({"ok": True, "result": result})
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
