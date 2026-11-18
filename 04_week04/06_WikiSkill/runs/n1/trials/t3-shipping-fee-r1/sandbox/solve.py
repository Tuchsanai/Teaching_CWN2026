import json
import sys
from fractions import Fraction


def _int(x, name, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"{name} must be an integer")
    if lo is not None and x < lo:
        raise ValueError(f"{name} must be >= {lo}")
    if hi is not None and x > hi:
        raise ValueError(f"{name} must be <= {hi}")
    return x


def _flag(x, name):
    if not isinstance(x, bool):
        raise ValueError(f"{name} must be a bool")
    return x


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee in integer satang."""
    _int(weight_g, "weight_g", 1, 30000)
    _int(distance_km, "distance_km", 0)
    _flag(express, "express")

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)

    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)

    num, den = fee.numerator, fee.denominator
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = shipping_fee(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
