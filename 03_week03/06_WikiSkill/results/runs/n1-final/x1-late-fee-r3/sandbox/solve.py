def _int(x, name, lo=None, hi=None):
    if type(x) is not int:
        raise ValueError(f"{name} must be an integer")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"{name} out of range")
    return x


def late_fee(amount, days_late):
    amount = _int(amount, "amount", 0)
    days_late = _int(days_late, "days_late", 0, 365)
    if days_late <= 3:
        return 0
    rate_bp = min(75 * days_late, 1500)  # basis points (1/10000)
    num, den = amount * rate_bp, 10000
    return (2 * num + den) // (2 * den)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = late_fee(**data)
        print(json.dumps({"ok": True, "result": result}))
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
