import json
import sys


def _check_int(value, name):
    if type(value) is not int:
        raise ValueError(name + " must be an int")


def late_fee(amount, days_late):
    _check_int(amount, "amount")
    _check_int(days_late, "days_late")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if days_late < 0 or days_late > 365:
        raise ValueError("days_late must be between 0 and 365")
    if days_late <= 3:
        return 0
    # rate in ten-thousandths: 75 per day, capped at 1500
    rate = min(75 * days_late, 1500)
    num = amount * rate
    den = 10000
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for key in ("amount", "days_late"):
            if key not in data:
                raise ValueError("missing key: " + key)
        result = late_fee(data["amount"], data["days_late"])
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
