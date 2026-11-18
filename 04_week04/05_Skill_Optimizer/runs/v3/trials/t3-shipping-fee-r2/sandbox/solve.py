import json
import sys
from fractions import Fraction


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def shipping_fee(weight_g, distance_km, express):
    if not _is_int(weight_g) or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be an int in 1..30000")
    if not _is_int(distance_km) or distance_km < 0:
        raise ValueError("distance_km must be an int >= 0")
    if not isinstance(express, bool):
        raise ValueError("express must be a bool")
    if express and weight_g > 20000:
        raise ValueError("express supports at most 20000 g")
    if distance_km == 0:
        return 0  # customer pickup
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 baht/kg = 1500 satang per 1000 g
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("weight_g", "distance_km", "express"):
            if k not in data:
                raise ValueError("missing key: " + k)
        result = shipping_fee(data["weight_g"], data["distance_km"], data["express"])
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
