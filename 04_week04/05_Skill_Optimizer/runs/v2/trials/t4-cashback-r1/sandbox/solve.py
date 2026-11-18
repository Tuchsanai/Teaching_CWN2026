import json
import sys

RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}
DOUBLE_TIERS = {"gold", "platinum"}
MIN_AMOUNT = 10000   # 100 baht, in satang
CAP = 20000          # 200 baht, in satang


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative int")
    if not isinstance(tier, str) or tier not in RATES_PERMILLE:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday and tier in DOUBLE_TIERS else 1
    result = amount * RATES_PERMILLE[tier] * mult // 1000  # floor
    return min(result, CAP)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("amount", "tier", "birthday"):
            if k not in data:
                raise ValueError("missing key: " + k)
        result = cashback(data["amount"], data["tier"], data["birthday"])
        print(json.dumps({"ok": True, "result": result}))
        return 0
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e) or "invalid input"}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
