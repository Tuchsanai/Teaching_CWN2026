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
    tip = (total * tip_percent + 50) // 100  # ปัดครึ่งขึ้น (จำนวนเต็มล้วน)
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("total", "people", "tip_percent"):
            if k not in data:
                raise ValueError(f"missing key: {k}")
        result = split_bill(data["total"], data["people"], data["tip_percent"])
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
