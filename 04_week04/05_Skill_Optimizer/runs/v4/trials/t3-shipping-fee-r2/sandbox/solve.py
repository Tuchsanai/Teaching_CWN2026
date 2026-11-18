import json
import sys
from fractions import Fraction


def _check_int(name, v):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be int")


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee in integer satang."""
    _check_int("weight_g", weight_g)
    _check_int("distance_km", distance_km)
    if not isinstance(express, bool):
        raise ValueError("express must be bool")
    if not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be 1-30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")
    if express and weight_g > 20000:
        raise ValueError("express allowed up to 20000 g")
    if distance_km == 0:
        return 0

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 baht/kg = 1500 satang/kg, prorated by gram
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    # single rounding at the end, half up
    return int((fee * 2 + 1) // 2)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        fee = shipping_fee(data.get("weight_g"), data.get("distance_km"),
                           data.get("express", False))
        print(json.dumps({"fee_satang": fee}))
    except (ValueError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
