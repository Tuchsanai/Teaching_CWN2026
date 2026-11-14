import json
import sys

RATES_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}
MIN_AMOUNT = 10000   # 100 baht in satang
MAX_CASHBACK = 20000  # 200 baht in satang


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative int (satang)")
    if type(tier) is not str or tier not in RATES_PER_MILLE:
        raise ValueError("tier must be 'silver', 'gold' or 'platinum'")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    # amount * rate/1000 * mult, rounded half up using integers only
    num = amount * RATES_PER_MILLE[tier] * mult
    result = (num * 2 + 1000) // 2000
    return min(result, MAX_CASHBACK)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("amount", "tier", "birthday"):
            if k not in data:
                raise ValueError("missing key: " + k)
        result = cashback(data["amount"], data["tier"], data["birthday"])
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
