"""BaanKafe shipping fee calculator.

shipping_fee(weight_g, distance_km, express) -> int (satang)

Rules:
- weight_g: integer 1..30000 grams
  - <= 1000 g          : 40 baht
  - 1001..5000 g       : 80 baht
  - > 5000 g           : 80 baht + 15 baht per kg of the excess over 5000 g
                         (prorated per gram)
- distance_km: number >= 0; > 100 km adds 20%
- express: True adds 50% (applied after the distance surcharge)
- result: integer satang, rounded half up exactly once at the end
"""

import sys
import json
import math
from fractions import Fraction

MAX_WEIGHT_G = 30000
DISTANCE_SURCHARGE_THRESHOLD_KM = 100
SATANG_PER_BAHT = 100


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


def _distance(v, name):
    # Distance is a measurement, not money: whole or fractional km are both allowed.
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError(f"{name} must be a number")
    if isinstance(v, float) and not math.isfinite(v):
        raise ValueError(f"{name} must be finite")
    if v < 0:
        raise ValueError(f"{name} out of range")
    # Convert via the decimal string so 12.5 becomes exactly 25/2, not a binary float.
    return Fraction(str(v))


def _half_up(x: Fraction) -> int:
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def shipping_fee(weight_g, distance_km, express):
    weight_g = _int(weight_g, "weight_g", 1, MAX_WEIGHT_G)
    distance = _distance(distance_km, "distance_km")
    express = _bool(express, "express")

    # Base fee in satang, kept as an exact Fraction (no rounding yet).
    if weight_g <= 1000:
        fee = Fraction(40 * SATANG_PER_BAHT)
    elif weight_g <= 5000:
        fee = Fraction(80 * SATANG_PER_BAHT)
    else:
        # 15 baht per kg = 1500 satang per 1000 g = 3/2 satang per gram.
        fee = Fraction(80 * SATANG_PER_BAHT) + Fraction(3 * (weight_g - 5000), 2)

    if distance > DISTANCE_SURCHARGE_THRESHOLD_KM:
        fee *= Fraction(6, 5)  # +20%

    if express:
        fee *= Fraction(3, 2)  # +50%

    return _half_up(fee)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = shipping_fee(**data)
        out = json.dumps({"ok": True, "result": result})
    except Exception as e:  # covers bad JSON, wrong/missing keys, ValueError
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
