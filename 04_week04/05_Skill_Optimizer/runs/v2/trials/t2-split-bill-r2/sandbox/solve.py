import json
import sys


def _check_int(v, lo, hi=None):
    if type(v) is not int or v < lo or (hi is not None and v > hi):
        raise ValueError("invalid input")


def split_bill(total, people, tip_percent):
    _check_int(total, 0)
    _check_int(people, 1)
    _check_int(tip_percent, 0, 100)
    tip = (total * tip_percent + 50) // 100  # ปัดครึ่งขึ้น
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        try:
            args = [data["total"], data["people"], data["tip_percent"]]
        except KeyError as e:
            raise ValueError("missing key: %s" % e)
        result = split_bill(*args)
        print(json.dumps({"ok": True, "result": result}))
        return 0
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e) or "error"}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
