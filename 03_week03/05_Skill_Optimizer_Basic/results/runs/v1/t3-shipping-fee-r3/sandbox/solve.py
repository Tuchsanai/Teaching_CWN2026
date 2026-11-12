import json
import sys
from fractions import Fraction


def _check_int(name, v):
    if type(v) is not int:
        raise ValueError(f"{name} must be an int")


def shipping_fee(weight_g, distance_km, express):
    _check_int("weight_g", weight_g)
    _check_int("distance_km", distance_km)
    if type(express) is not bool:
        raise ValueError("express must be a bool")
    if not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 baht/kg = 1500 satang per 1000 g
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    # round half up, once, in exact arithmetic
    return int((fee * 2 + 1) // 2)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("weight_g", "distance_km", "express"):
            if k not in data:
                raise ValueError(f"missing key: {k}")
        result = shipping_fee(data["weight_g"], data["distance_km"], data["express"])
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
