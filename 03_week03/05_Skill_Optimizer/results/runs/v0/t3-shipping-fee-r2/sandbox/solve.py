"""BaanKafe shipping fee. All money is integer satang (no float arithmetic)."""
import json
import math
import sys
from fractions import Fraction


def _num(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return Fraction(str(value)) if isinstance(value, float) else Fraction(value)


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee in integer satang (rounded half up once, at the end)."""
    w = _num(weight_g, "weight_g")
    d = _num(distance_km, "distance_km")
    if not 1 <= w <= 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if d < 0:
        raise ValueError("distance_km must be >= 0")
    if not isinstance(express, bool):
        raise ValueError("express must be a boolean")

    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + (w - 5000) * Fraction(1500, 1000)  # 15 baht/kg
    if d > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return math.floor(fee + Fraction(1, 2))


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        missing = [k for k in ("weight_g", "distance_km", "express") if k not in data]
        if missing:
            raise ValueError("missing: " + ", ".join(missing))
        fee = shipping_fee(data["weight_g"], data["distance_km"], data["express"])
        print(json.dumps({"fee_satang": fee}))
    except (ValueError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
