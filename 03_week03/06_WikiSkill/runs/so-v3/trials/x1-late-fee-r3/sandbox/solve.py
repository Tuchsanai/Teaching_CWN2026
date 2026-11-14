import json
import sys


def _check_int(v, name, lo, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    if v < lo or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")


def late_fee(amount, days_late):
    _check_int(amount, "amount", 0)
    _check_int(days_late, "days_late", 0, 365)
    if days_late <= 3:
        return 0
    # rate in 1/10000 units: 0.75%/day, capped at 15%
    rate = min(75 * days_late, 1500)
    num = amount * rate
    den = 10000
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        if "amount" not in data or "days_late" not in data:
            raise ValueError("missing key")
        out = {"ok": True, "result": late_fee(data["amount"], data["days_late"])}
        code = 0
    except Exception as e:
        out = {"ok": False, "error": str(e)}
        code = 2
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(code)


if __name__ == "__main__":
    main()
