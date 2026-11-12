import json
import sys


def _is_int(v):
    return type(v) is int


def shipping_fee(weight_g, distance_km, express):
    if not _is_int(weight_g) or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be int 1-30000")
    if not _is_int(distance_km) or distance_km < 0:
        raise ValueError("distance_km must be int >= 0")
    if type(express) is not bool:
        raise ValueError("express must be bool")

    # base fee in satang * 1000 (keeps the per-gram fraction exact)
    if weight_g <= 1000:
        num = 4000 * 1000
    elif weight_g <= 5000:
        num = 8000 * 1000
    else:
        num = 8000 * 1000 + (weight_g - 5000) * 1500
    den = 1000
    if distance_km > 100:
        num *= 120
        den *= 100
    if express:
        num *= 150
        den *= 100
    # round half up, once at the end
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = shipping_fee(data["weight_g"], data["distance_km"], data["express"])
    except KeyError as e:
        print(json.dumps({"ok": False, "error": "missing key: %s" % e.args[0]}))
        return 2
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e) or "invalid input"}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
