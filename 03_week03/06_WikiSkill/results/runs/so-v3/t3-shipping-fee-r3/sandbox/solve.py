import json
import sys


def _check_int(v, name):
    if type(v) is not int:
        raise ValueError(name + " must be int")


def shipping_fee(weight_g, distance_km, express):
    _check_int(weight_g, "weight_g")
    _check_int(distance_km, "distance_km")
    if type(express) is not bool:
        raise ValueError("express must be bool")
    if weight_g < 1 or weight_g > 30000:
        raise ValueError("weight_g out of range")
    if distance_km < 0:
        raise ValueError("distance_km out of range")
    # satang, kept as fraction num/den (no intermediate rounding)
    if weight_g <= 1000:
        num, den = 4000, 1
    elif weight_g <= 5000:
        num, den = 8000, 1
    else:
        # 15 baht/kg = 1.5 satang/g
        num, den = 8000 * 2 + 3 * (weight_g - 5000), 2
    if distance_km > 100:
        num, den = num * 120, den * 100
    if express:
        num, den = num * 150, den * 100
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("weight_g", "distance_km", "express"):
            if k not in data:
                raise ValueError("missing key: " + k)
        result = shipping_fee(data["weight_g"], data["distance_km"], data["express"])
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
