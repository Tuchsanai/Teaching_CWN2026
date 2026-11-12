import json
import sys


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def bulk_price(unit_price, qty, coupon):
    if not _is_int(unit_price) or unit_price < 0:
        raise ValueError("unit_price must be int >= 0")
    if not _is_int(qty) or qty < 1 or qty > 1000:
        raise ValueError("qty must be int in 1..1000")
    if not isinstance(coupon, bool):
        raise ValueError("coupon must be bool")

    if qty >= 50:
        tier = 75
    elif qty >= 10:
        tier = 35
    else:
        tier = 0
    coupon_rate = 25 if coupon else 0

    # rates as integer fractions: tier per 1000, coupon per 1000, VAT 107 per 100
    num = unit_price * qty * (1000 - tier) * (1000 - coupon_rate) * 107
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("unit_price", "qty", "coupon"):
            if k not in data:
                raise ValueError("missing key: " + k)
        result = bulk_price(data["unit_price"], data["qty"], data["coupon"])
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
