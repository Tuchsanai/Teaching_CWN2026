"""BaanKafe cashback calculator. All money is integer satang (no floats)."""
import json
import sys

RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 10000   # 100 baht
MAX_CASHBACK = 20000  # 200 baht per bill


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount must be an integer number of satang")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not isinstance(tier, str) or tier not in RATES_PERMILLE:
        raise ValueError("tier must be one of: silver, gold, platinum")
    if not isinstance(birthday, bool):
        raise TypeError("birthday must be a boolean")

    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    # exact: amount * permille * mult / 1000, rounded half up once, in integers
    num = amount * RATES_PERMILLE[tier] * mult
    result = (num * 2 + 1000) // 2000
    return min(result, MAX_CASHBACK)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        raw = argv[0] if argv else sys.stdin.read()
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        missing = [k for k in ("amount", "tier", "birthday") if k not in data]
        if missing:
            raise ValueError("missing field(s): " + ", ".join(missing))
        out = {"cashback": cashback(data["amount"], data["tier"], data["birthday"])}
        print(json.dumps(out))
        return 0
    except (ValueError, TypeError) as e:  # includes JSON decode errors
        print(json.dumps({"error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
