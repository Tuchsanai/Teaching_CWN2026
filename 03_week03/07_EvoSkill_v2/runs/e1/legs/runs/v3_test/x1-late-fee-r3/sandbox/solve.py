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


def late_fee(amount, days_late):
    _need_int(amount, "amount", low=0)
    _need_int(days_late, "days_late", low=0, high=365)
    if days_late <= 3:
        return 0
    fee = Fraction(amount) * Fraction(75, 10000) * days_late
    fee = min(fee, Fraction(amount) * Fraction(15, 100))
    return _half_up(fee)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = late_fee(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
