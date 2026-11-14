import json
import sys
from fractions import Fraction


def _is_int(v):
    return type(v) is int


def shipping_fee(weight_g, distance_km, express):
    if not _is_int(weight_g) or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be an int between 1 and 30000")
    if not _is_int(distance_km) or distance_km < 0:
        raise ValueError("distance_km must be an int >= 0")
    if type(express) is not bool:
        raise ValueError("express must be a bool")

    # all money in satang, exact arithmetic, rounded half-up once at the end
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return (fee * 2 + 1) // 2


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("weight_g", "distance_km", "express"):
            if k not in data:
                raise ValueError("missing key: " + k)
        result = int(shipping_fee(data["weight_g"], data["distance_km"], data["express"]))
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
