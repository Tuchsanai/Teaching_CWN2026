import json
import sys


def _check_int(v, name, lo, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} must be an int")
    if v < lo or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")


def split_bill(total, people, tip_percent):
    _check_int(total, "total", 0)
    _check_int(people, "people", 1)
    _check_int(tip_percent, "tip_percent", 0, 100)
    tip = (total * tip_percent * 2 + 100) // 200  # ปัดครึ่งขึ้น
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = split_bill(data["total"], data["people"], data["tip_percent"])
    except KeyError as e:
        print(json.dumps({"ok": False, "error": f"missing key: {e.args[0]}"}))
        return 2
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
