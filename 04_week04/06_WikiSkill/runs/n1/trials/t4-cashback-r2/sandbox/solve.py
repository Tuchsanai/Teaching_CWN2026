import json
import sys

_RATES = {"silver": (3, 200), "gold": (1, 40), "platinum": (1, 25)}
_MIN_AMOUNT = 10000   # 100 บาท
_CAP = 20000          # 200 บาท


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("amount must be an integer")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError("tier must be one of silver, gold, platinum")
    if not isinstance(birthday, bool):
        raise ValueError("birthday must be a bool")

    if amount < _MIN_AMOUNT:
        return 0
    n, d = _RATES[tier]
    if birthday:
        n *= 2
    num = amount * n
    result = (2 * num + d) // (2 * d)  # half up ครั้งเดียว
    return min(result, _CAP)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cashback(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
