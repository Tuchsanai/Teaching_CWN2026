"""BaanKafe bill splitter. All money is integer satang (no floats)."""
import json
import sys


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def split_bill(total, people, tip_percent):
    if not _is_int(total) or total < 0:
        raise ValueError("total must be an integer >= 0")
    if not _is_int(people) or people < 1:
        raise ValueError("people must be an integer >= 1")
    if not _is_int(tip_percent) or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be an integer between 0 and 100")

    # tip rounded to nearest satang, half up (integer arithmetic only)
    tip = (total * tip_percent + 50) // 100
    grand = total + tip
    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]


def main(argv):
    try:
        raw = argv[1] if len(argv) > 1 else sys.stdin.read()
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        missing = [k for k in ("total", "people", "tip_percent") if k not in data]
        if missing:
            raise ValueError("missing fields: " + ", ".join(missing))
        result = split_bill(data["total"], data["people"], data["tip_percent"])
        print(json.dumps({"shares": result}))
        return 0
    except (ValueError, TypeError) as e:
        print(json.dumps({"error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
