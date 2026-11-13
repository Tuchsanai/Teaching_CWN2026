import json
import sys
from fractions import Fraction


def _half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def bulk_price(unit_price, qty, coupon):
    if type(unit_price) is not int or unit_price < 0:
        raise ValueError("unit_price ต้องเป็นจำนวนเต็มตั้งแต่ 0")
    if type(qty) is not int or qty < 1 or qty > 1000:
        raise ValueError("qty ต้องเป็นจำนวนเต็ม 1 ถึง 1000")
    if type(coupon) is not bool:
        raise ValueError("coupon ต้องเป็น True หรือ False")

    total = Fraction(unit_price * qty)
    if qty >= 50:
        total *= Fraction(925, 1000)
    elif qty >= 10:
        total *= Fraction(965, 1000)
    if coupon:
        total *= Fraction(975, 1000)
    total *= Fraction(107, 100)
    return _half_up(total)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = bulk_price(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
