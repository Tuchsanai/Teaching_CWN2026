import json
import sys


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def shipping_fee(weight_g, distance_km, express):
    if not _is_int(weight_g) or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be an int between 1 and 30000")
    if not _is_int(distance_km) or distance_km < 0:
        raise ValueError("distance_km must be an int >= 0")
    if not isinstance(express, bool):
        raise ValueError("express must be a bool")

    # base fee in satang, kept as numerator over 2
    if weight_g <= 1000:
        base = 4000 * 2
    elif weight_g <= 5000:
        base = 8000 * 2
    else:
        # 15 baht/kg = 3/2 satang per gram
        base = 8000 * 2 + 3 * (weight_g - 5000)
    num = base * (6 if distance_km > 100 else 5) * (3 if express else 2)
    den = 2 * 5 * 2
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
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
