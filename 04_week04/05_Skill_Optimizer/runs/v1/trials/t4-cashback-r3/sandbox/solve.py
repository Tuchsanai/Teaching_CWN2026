import json
import sys

RATES = {"silver": 15, "gold": 25, "platinum": 40}  # per 1000
MIN_AMOUNT = 10000   # 100 baht in satang
CAP = 20000          # 200 baht in satang


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative int")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < MIN_AMOUNT:
        return 0
    num = amount * RATES[tier] * (2 if birthday else 1)
    result = (num + 500) // 1000  # round half up, integer only
    return min(result, CAP)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cashback(data["amount"], data["tier"], data["birthday"])
        print(json.dumps({"ok": True, "result": result}))
        return 0
    except Exception as e:
        msg = "missing key: %s" % e if isinstance(e, KeyError) else str(e)
        print(json.dumps({"ok": False, "error": msg}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
