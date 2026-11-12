import json
import sys

RATES = {"silver": 15, "gold": 25, "platinum": 40}  # ต่อ 1000
MIN_AMOUNT = 10000  # 100 บาท
CAP = 20000  # 200 บาท


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative int")
    if not isinstance(tier, str) or tier not in RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
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
        for k in ("amount", "tier", "birthday"):
            if k not in data:
                raise ValueError("missing key: " + k)
        out = {"ok": True, "result": cashback(data["amount"], data["tier"], data["birthday"])}
        code = 0
    except (ValueError, RecursionError) as e:
        out = {"ok": False, "error": str(e)}
        code = 2
    print(json.dumps(out))
    sys.exit(code)


if __name__ == "__main__":
    main()
