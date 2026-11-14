import json
import sys


def _check_int(v, lo, hi=None):
    if type(v) is not int or v < lo or (hi is not None and v > hi):
        raise ValueError("invalid input")


def split_bill(total, people, tip_percent):
    _check_int(total, 0)
    _check_int(people, 1)
    _check_int(tip_percent, 0, 100)
    num = total * (100 + tip_percent)
    den = 100
    grand = (2 * num + den) // (2 * den)  # round half up, once
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = split_bill(data["total"], data["people"], data["tip_percent"])
        print(json.dumps({"ok": True, "result": result}))
        return 0
    except (ValueError, KeyError) as e:
        print(json.dumps({"ok": False, "error": "invalid input: %s" % e}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
