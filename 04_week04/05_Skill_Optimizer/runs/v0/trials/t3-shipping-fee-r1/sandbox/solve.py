"""BaanKafe shipping fee. Money is integer satang; no floats in calculation."""
import json
import math
import sys
from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    if isinstance(weight_g, bool) or not isinstance(weight_g, (int, float, Fraction)):
        raise ValueError("weight_g must be a number")
    if isinstance(weight_g, float) and not math.isfinite(weight_g):
        raise ValueError("weight_g must be finite")
    if not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if isinstance(distance_km, bool) or not isinstance(distance_km, (int, float, Fraction)):
        raise ValueError("distance_km must be a number")
    if isinstance(distance_km, float) and not math.isfinite(distance_km):
        raise ValueError("distance_km must be finite")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")
    if not isinstance(express, bool):
        raise ValueError("express must be a boolean")

    w = Fraction(weight_g)
    d = Fraction(distance_km)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)  # 15 baht/kg
    if d > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    # round half up to whole satang, once, at the end
    return math.floor(fee + Fraction(1, 2))


def main():
    try:
        data = json.load(sys.stdin)
        satang = shipping_fee(data["weight_g"], data["distance_km"], data["express"])
        print(json.dumps({"fee_satang": satang}))
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({"error": f"{type(e).__name__}: {e}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
