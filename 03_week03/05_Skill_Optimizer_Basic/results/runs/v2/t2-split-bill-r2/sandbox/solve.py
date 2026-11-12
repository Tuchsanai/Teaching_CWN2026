import json
import sys


def _check_int(name, value, lo, hi=None):
    if type(value) is not int:
        raise ValueError(f"{name} must be an integer")
    if value < lo or (hi is not None and value > hi):
        raise ValueError(f"{name} out of range")


def split_bill(total, people, tip_percent):
    _check_int("total", total, 0)
    _check_int("people", people, 1)
    _check_int("tip_percent", tip_percent, 0, 100)

    # total with tip = total * (100 + tip_percent) over 100, rounded half-up once
    num = total * (100 + tip_percent)
    den = 100
    grand = (2 * num + den) // (2 * den)

    base, extra = grand // people, grand % people
    return [base + 1 if i < extra else base for i in range(people)]


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for key in ("total", "people", "tip_percent"):
            if key not in data:
                raise ValueError(f"missing key: {key}")
        result = split_bill(data["total"], data["people"], data["tip_percent"])
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
