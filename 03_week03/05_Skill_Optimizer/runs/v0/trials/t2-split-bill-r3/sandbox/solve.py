import json
import sys


def _check_int(name, value, lo, hi=None):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if value < lo or (hi is not None and value > hi):
        rng = f">= {lo}" if hi is None else f"between {lo} and {hi}"
        raise ValueError(f"{name} must be {rng}")


def split_bill(total, people, tip_percent):
    _check_int("total", total, 0)
    _check_int("people", people, 1)
    _check_int("tip_percent", tip_percent, 0, 100)
    # tip rounded half up to whole satang, integer math only
    tip = (total * tip_percent + 50) // 100
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        raw = argv[0] if argv else sys.stdin.read()
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        missing = {"total", "people", "tip_percent"} - data.keys()
        if missing:
            raise ValueError(f"missing field(s): {', '.join(sorted(missing))}")
        result = split_bill(data["total"], data["people"], data["tip_percent"])
    except (ValueError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
