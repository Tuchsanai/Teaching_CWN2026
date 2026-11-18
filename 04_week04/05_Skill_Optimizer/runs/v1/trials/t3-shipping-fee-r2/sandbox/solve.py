import json
import sys


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

    # exact arithmetic: value = num / den satang, round half up once at the end
    num, den = 4000 if weight_g <= 1000 else 8000, 1
    if weight_g > 5000:
        num, den = 8000 * 2 + (weight_g - 5000) * 3, 2  # 1.5 satang per gram
    if distance_km > 100:
        num, den = num * 120, den * 100
    if express:
        num, den = num * 150, den * 100
    return (2 * num + den) // (2 * den)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = shipping_fee(data["weight_g"], data["distance_km"], data["express"])
        print(json.dumps({"ok": True, "result": result}))
    except (ValueError, KeyError) as e:
        print(json.dumps({"ok": False, "error": "missing key: %s" % e if isinstance(e, KeyError) else str(e)}))
        sys.exit(2)


if __name__ == "__main__":
    _main()
