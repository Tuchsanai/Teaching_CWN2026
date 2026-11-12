import json
import sys


def shipping_fee(weight_g, distance_km, express):
    for v in (weight_g, distance_km):
        if type(v) is not int:
            raise ValueError("weight_g and distance_km must be int")
    if type(express) is not bool:
        raise ValueError("express must be bool")
    if weight_g < 1 or weight_g > 30000:
        raise ValueError("weight_g must be in 1..30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    # satang, as fraction num/den
    if weight_g <= 1000:
        num, den = 4000, 1
    elif weight_g <= 5000:
        num, den = 8000, 1
    else:
        # 15 baht/kg = 1500 satang / 1000 g = 3/2 satang per gram
        num, den = 16000 + 3 * (weight_g - 5000), 2
    if distance_km > 100:
        num, den = num * 6, den * 5
    if express:
        num, den = num * 3, den * 2
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = shipping_fee(data["weight_g"], data["distance_km"], data["express"])
    except KeyError as e:
        print(json.dumps({"ok": False, "error": "missing key: %s" % e.args[0]}))
        sys.exit(2)
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
