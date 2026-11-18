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


def _flag(x, name):
    if not isinstance(x, bool):
        raise ValueError(f"{name} must be a bool")
    return x


def bulk_price(unit_price, qty, coupon):
    _int(unit_price, "unit_price", lo=0)
    _int(qty, "qty", lo=1, hi=1000)
    _flag(coupon, "coupon")

    if qty >= 50:
        tier = 925  # ลด 7.5%
    elif qty >= 10:
        tier = 965  # ลด 3.5%
    else:
        tier = 1000
    coup = 975 if coupon else 1000  # ลดอีก 2.5%

    num = unit_price * qty * tier * coup * 107  # VAT 7%
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)  # half up ครั้งเดียว


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
