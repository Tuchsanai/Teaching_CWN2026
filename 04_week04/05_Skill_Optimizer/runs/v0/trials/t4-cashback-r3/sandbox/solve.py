"""BaanKafe member cashback. All money is integer satang; no floats."""
import json
import sys

RATE_BP = {"silver": 150, "gold": 250, "platinum": 400}  # basis points (1/100 of %)
MIN_AMOUNT = 100_00   # 100 baht
MAX_CASHBACK = 200_00  # 200 baht per bill


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("amount must be an integer number of satang")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not isinstance(tier, str) or tier not in RATE_BP:
        raise ValueError("tier must be one of: silver, gold, platinum")
    if not isinstance(birthday, bool):
        raise ValueError("birthday must be a boolean")

    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    # round half up, once, in pure integer arithmetic
    num = amount * RATE_BP[tier] * mult
    result = (num * 2 + 10_000) // 20_000
    return min(result, MAX_CASHBACK)


def main(argv):
    try:
        raw = argv[1] if len(argv) > 1 else sys.stdin.read()
        data = json.loads(raw)
        if not isinstance(data, dict) or not {"amount", "tier", "birthday"} <= data.keys():
            raise ValueError("input must be a JSON object with amount, tier, birthday")
        out = {"cashback": cashback(data["amount"], data["tier"], data["birthday"])}
        print(json.dumps(out))
        return 0
    except (ValueError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
