import json
import sys
from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    for v in (weight_g, distance_km):
        if type(v) is not int:
            raise ValueError("weight_g and distance_km must be int")
    if type(express) is not bool:
        raise ValueError("express must be bool")
    if not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be 1-30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")
    if express and weight_g > 20000:
        raise ValueError("express supports weight up to 20000 g")
    if distance_km == 0:
        return 0  # customer pickup

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
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = shipping_fee(data["weight_g"], data["distance_km"], data["express"])
        print(json.dumps({"ok": True, "result": result}))
        return 0
    except (ValueError, KeyError) as e:
        print(json.dumps({"ok": False, "error": "missing key: %s" % e if isinstance(e, KeyError) else str(e)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
