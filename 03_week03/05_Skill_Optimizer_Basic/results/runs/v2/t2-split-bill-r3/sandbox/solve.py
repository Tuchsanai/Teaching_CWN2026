import json
import sys


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def split_bill(total, people, tip_percent):
    if not _is_int(total) or total < 0:
        raise ValueError("total must be an int >= 0")
    if not _is_int(people) or people < 1:
        raise ValueError("people must be an int >= 1")
    if not _is_int(tip_percent) or tip_percent < 0 or tip_percent > 100:
        raise ValueError("tip_percent must be an int between 0 and 100")
    num = total * (100 + tip_percent)
    den = 100
    grand = (2 * num + den) // (2 * den)  # half-up, single rounding step
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("total", "people", "tip_percent"):
            if k not in data:
                raise ValueError("missing key: " + k)
        result = split_bill(data["total"], data["people"], data["tip_percent"])
    except ValueError as e:  # includes JSON decode errors
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
