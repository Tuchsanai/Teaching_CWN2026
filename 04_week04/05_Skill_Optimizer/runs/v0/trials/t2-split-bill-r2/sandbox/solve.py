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
    tip = (total * tip_percent + 50) // 100  # round half up, integer only
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main(argv):
    try:
        raw = argv[1] if len(argv) > 1 else sys.stdin.read()
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("total", "people", "tip_percent"):
            if k not in data:
                raise ValueError(f"missing field: {k}")
        result = split_bill(data["total"], data["people"], data["tip_percent"])
    except ValueError as e:  # includes JSONDecodeError
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
