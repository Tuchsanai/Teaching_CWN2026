import json
import sys
from fractions import Fraction


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def shipping_fee(weight_g, distance_km, express):
    if not _is_int(weight_g) or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be int in 1..30000")
    if not _is_int(distance_km) or distance_km < 0:
        raise ValueError("distance_km must be int >= 0")
    if not isinstance(express, bool):
        raise ValueError("express must be bool")
    if express and weight_g > 20000:
        raise ValueError("express weight must not exceed 20000 g")
    if distance_km == 0:
        return 0  # customer pickup
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + Fraction((weight_g - 5000) * 3, 2)  # 1.5 satang/g
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return int((fee * 2 + 1) // 2)  # round half up, once at the end


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        args = [data[k] for k in ("weight_g", "distance_km", "express")]
        out = {"ok": True, "result": shipping_fee(*args)}
        code = 0
    except (ValueError, KeyError, TypeError) as e:
        out = {"ok": False, "error": "missing key %s" % e if isinstance(e, KeyError) else str(e)}
        code = 2
    print(json.dumps(out))
    sys.exit(code)


if __name__ == "__main__":
    main()
