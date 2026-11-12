import json
import sys

# อัตราเป็นเศษส่วน (n, d)
_RATES = {"silver": (3, 200), "gold": (1, 40), "platinum": (1, 25)}
_MIN_AMOUNT = 10000  # 100 บาท (สตางค์)
_CAP = 20000         # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be int >= 0")
    if type(tier) is not str or tier not in _RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")

    if amount < _MIN_AMOUNT:
        return 0
    n, d = _RATES[tier]
    n *= amount * (2 if birthday else 1)
    result = (2 * n + d) // (2 * d)  # half-up ครั้งเดียว
    return min(result, _CAP)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = cashback(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
