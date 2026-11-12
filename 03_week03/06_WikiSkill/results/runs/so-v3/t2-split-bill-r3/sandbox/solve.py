import json
import sys


def _check_int(name, value, low, high=None):
    if type(value) is not int:
        raise ValueError(name + " must be an int")
    if value < low or (high is not None and value > high):
        raise ValueError(name + " out of range")


def split_bill(total, people, tip_percent):
    _check_int("total", total, 0)
    _check_int("people", people, 1)
    _check_int("tip_percent", tip_percent, 0, 100)
    num = total * (100 + tip_percent)
    den = 100
    grand = (2 * num + den) // (2 * den)  # half-up, rounded once
    base = grand // people
    extra = grand % people
    return [base + 1 if i < extra else base for i in range(people)]


def main():
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("input must be a JSON object")
        for key in ("total", "people", "tip_percent"):
            if key not in data:
                raise ValueError("missing key: " + key)
        result = split_bill(data["total"], data["people"], data["tip_percent"])
    except (ValueError, RecursionError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
