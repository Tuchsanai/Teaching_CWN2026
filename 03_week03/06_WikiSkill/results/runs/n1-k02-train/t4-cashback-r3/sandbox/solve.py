RATES = {"silver": (15, 1000), "gold": (25, 1000), "platinum": (4, 100)}
MIN_AMOUNT = 10000  # 100 baht in satang
CAP = 20000         # 200 baht in satang


def cashback(amount, tier, birthday):
    if type(amount) is not int:
        raise ValueError("amount must be an integer")
    if amount < 0:
        raise ValueError("amount out of range")
    if type(birthday) is not bool:
        raise ValueError("birthday must be a boolean")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("unknown tier")
    if amount < MIN_AMOUNT:
        return 0
    n, d = RATES[tier]
    if birthday:
        n *= 2
    num, den = amount * n, d
    result = (2 * num + den) // (2 * den)  # half-up
    return min(result, CAP)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cashback(**data)
        print(json.dumps({"ok": True, "result": result}))
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
