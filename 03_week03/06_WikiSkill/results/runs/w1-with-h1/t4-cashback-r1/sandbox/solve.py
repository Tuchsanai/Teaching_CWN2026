import sys
import json
from fractions import Fraction

_RATES = {
    "silver": Fraction(15, 1000),
    "gold": Fraction(25, 1000),
    "platinum": Fraction(4, 100),
}
_MIN_AMOUNT = 10000  # 100 baht in satang
_CAP = 20000         # 200 baht in satang


def _half_up(x: Fraction) -> int:
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("amount must be an integer")
    if amount < 0:
        raise ValueError("amount out of range")
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError("tier must be one of silver, gold, platinum")
    if not isinstance(birthday, bool):
        raise ValueError("birthday must be a bool")

    if amount < _MIN_AMOUNT:
        return 0
    value = amount * _RATES[tier] * (2 if birthday else 1)
    return min(_half_up(value), _CAP)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cashback(**data)
        out = json.dumps({"ok": True, "result": result})
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
