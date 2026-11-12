import json
import sys

# rate as numerator over 1000 (silver 1.5%, gold 2.5%, platinum 4%)
RATES = {"silver": 15, "gold": 25, "platinum": 40}
MIN_AMOUNT = 10000   # 100 baht in satang
CAP = 20000          # 200 baht in satang


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be an int >= 0")
    if not isinstance(tier, str) or tier not in RATES:
        raise ValueError("tier must be silver, gold or platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday must be a bool")
    if amount < MIN_AMOUNT:
        return 0
    num = amount * RATES[tier] * (2 if birthday else 1)
    den = 1000
    result = (2 * num + den) // (2 * den)
    return min(result, CAP)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for key in ("amount", "tier", "birthday"):
            if key not in data:
                raise ValueError("missing key: " + key)
        result = cashback(data["amount"], data["tier"], data["birthday"])
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
