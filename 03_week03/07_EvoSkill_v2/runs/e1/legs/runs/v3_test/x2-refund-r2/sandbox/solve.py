import json
import sys
from fractions import Fraction


def _need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def _half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def refund(paid, used_percent, restock):
    _need_int(paid, "paid", low=0)
    _need_int(used_percent, "used_percent", low=0, high=100)
    if type(restock) is not bool:
        raise ValueError("restock ต้องเป็น True หรือ False")
    if used_percent > 80:
        return 0
    amount = Fraction(paid) * (100 - used_percent) / 100
    if restock:
        amount *= Fraction(875, 1000)
    return _half_up(amount)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = refund(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
