import json
import sys
from fractions import Fraction


def late_fee(amount, days_late):
    for v in (amount, days_late):
        if type(v) is not int:
            raise ValueError("input must be int")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not 0 <= days_late <= 365:
        raise ValueError("days_late must be in 0..365")
    if days_late <= 3:
        return 0
    fee = Fraction(amount * 75 * days_late, 10000)
    cap = Fraction(amount * 15, 100)
    if fee > cap:
        fee = cap
    n, d = fee.numerator, fee.denominator
    return (2 * n + d) // (2 * d)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        if "amount" not in data or "days_late" not in data:
            raise ValueError("missing key")
        result = late_fee(data["amount"], data["days_late"])
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
