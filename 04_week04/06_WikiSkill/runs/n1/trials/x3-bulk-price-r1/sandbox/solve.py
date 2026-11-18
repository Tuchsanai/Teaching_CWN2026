import json
import sys


def _int(x, name, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"{name} must be an integer")
    if lo is not None and x < lo:
        raise ValueError(f"{name} must be >= {lo}")
    if hi is not None and x > hi:
        raise ValueError(f"{name} must be <= {hi}")
    return x


def bulk_price(unit_price, qty, coupon):
    _int(unit_price, "unit_price", lo=0)
    _int(qty, "qty", lo=1, hi=1000)
    if not isinstance(coupon, bool):
        raise ValueError("coupon must be a bool")

    num = unit_price * qty
    den = 1
    if qty >= 50:
        num *= 925
        den *= 1000
    elif qty >= 10:
        num *= 965
        den *= 1000
    if coupon:
        num *= 975
        den *= 1000
    num *= 107
    den *= 100
    # half up, rounded once at the end
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = bulk_price(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
