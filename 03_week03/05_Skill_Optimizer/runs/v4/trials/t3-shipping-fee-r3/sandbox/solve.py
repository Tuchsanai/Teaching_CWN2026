import json
import sys


def _check_int(name, value, lo, hi=None):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be int")
    if value < lo or (hi is not None and value > hi):
        raise ValueError(f"{name} out of range")


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee in integer satang (round half up, once at the end)."""
    _check_int("weight_g", weight_g, 1, 30000)
    _check_int("distance_km", distance_km, 0)
    if not isinstance(express, bool):
        raise ValueError("express must be bool")
    if express and weight_g > 20000:
        raise ValueError("express not allowed over 20000 g")
    if distance_km == 0:
        return 0

    # base in satang * 1000 (exact): 15 baht/kg = 1500 satang per 1000 g
    if weight_g <= 1000:
        base = 4000 * 1000
    elif weight_g <= 5000:
        base = 8000 * 1000
    else:
        base = 8000 * 1000 + (weight_g - 5000) * 1500

    num = base * (120 if distance_km > 100 else 100) * (150 if express else 100)
    den = 1000 * 100 * 100
    return (2 * num + den) // (2 * den)  # half up


def main():
    try:
        data = json.load(sys.stdin)
        fee = shipping_fee(data["weight_g"], data["distance_km"], data["express"])
        print(json.dumps({"fee_satang": fee}))
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
