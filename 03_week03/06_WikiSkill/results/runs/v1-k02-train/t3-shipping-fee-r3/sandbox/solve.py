import json, sys


def _int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def shipping_fee(weight_g, distance_km, express):
    _int("weight_g", weight_g, 1, 30000)
    _int("distance_km", distance_km, 0)
    if type(express) is not bool:
        raise ValueError("express must be bool")

    # fee in satang as fraction n/d
    if weight_g <= 1000:
        n, d = 4000, 1
    elif weight_g <= 5000:
        n, d = 8000, 1
    else:
        n, d = (80000 + 15 * (weight_g - 5000)) * 100, 1000
    if distance_km > 100:
        n, d = n * 6, d * 5
    if express:
        n, d = n * 3, d * 2
    return (2 * n + d) // (2 * d)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = shipping_fee(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
