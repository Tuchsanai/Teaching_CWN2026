"""BaanKafe member cashback. All money is integer satang (no floats).

CLI: echo '{"amount": 50000, "tier": "gold", "birthday": false}' | python solve.py
     python solve.py '{"amount": 50000, "tier": "gold", "birthday": false}'
"""
import json
import sys

# rate as (numerator, denominator): silver 1.5%, gold 2.5%, platinum 4%
_RATES = {"silver": (15, 1000), "gold": (25, 1000), "platinum": (40, 1000)}
MIN_AMOUNT = 100 * 100   # 100 baht in satang
MAX_CASHBACK = 200 * 100  # 200 baht in satang


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount must be an integer number of satang")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError("tier must be one of: silver, gold, platinum")
    if not isinstance(birthday, bool):
        raise TypeError("birthday must be a boolean")

    if amount < MIN_AMOUNT:
        return 0
    num, den = _RATES[tier]
    if birthday:
        num *= 2
    # round half up using integer arithmetic
    result = (amount * num * 2 + den) // (den * 2)
    return min(result, MAX_CASHBACK)


def main(argv):
    raw = argv[1] if len(argv) > 1 else sys.stdin.read()
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        missing = [k for k in ("amount", "tier", "birthday") if k not in data]
        if missing:
            raise ValueError("missing field(s): " + ", ".join(missing))
        out = {"cashback": cashback(data["amount"], data["tier"], data["birthday"])}
        code = 0
    except (ValueError, TypeError) as e:  # includes JSONDecodeError
        out, code = {"error": str(e)}, 1
    print(json.dumps(out, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
