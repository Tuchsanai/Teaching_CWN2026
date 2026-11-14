import json
import sys
from fractions import Fraction


def bulk_price(unit_price, qty, coupon):
    if type(unit_price) is not int or unit_price < 0:
        raise ValueError("unit_price must be an int >= 0")
    if type(qty) is not int or not 1 <= qty <= 1000:
        raise ValueError("qty must be an int between 1 and 1000")
    if type(coupon) is not bool:
        raise ValueError("coupon must be a bool")

    total = Fraction(unit_price * qty)
    if qty >= 50:
        total *= Fraction(1000 - 75, 1000)
    elif qty >= 10:
        total *= Fraction(1000 - 35, 1000)
    if coupon:
        total *= Fraction(1000 - 25, 1000)
    total *= Fraction(107, 100)

    n, d = total.numerator, total.denominator
    return (2 * n + d) // (2 * d)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("unit_price", "qty", "coupon"):
            if k not in data:
                raise ValueError("missing key: " + k)
        result = bulk_price(data["unit_price"], data["qty"], data["coupon"])
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
