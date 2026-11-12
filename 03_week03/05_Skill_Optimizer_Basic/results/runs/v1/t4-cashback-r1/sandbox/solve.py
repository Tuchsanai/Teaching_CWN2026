import json
import sys

# อัตราเงินคืนหน่วยต่อ 1000 (silver 1.5% = 15/1000)
_RATES = {"silver": 15, "gold": 25, "platinum": 40}
_MIN_AMOUNT = 10000  # 100 บาท (สตางค์)
_CAP = 20000  # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if type(amount) is not int:
        raise ValueError("amount must be an int")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if type(tier) is not str or tier not in _RATES:
        raise ValueError("tier must be 'silver', 'gold' or 'platinum'")
    if type(birthday) is not bool:
        raise ValueError("birthday must be a bool")

    if amount < _MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    # ปัดครึ่งขึ้นด้วยเลขจำนวนเต็มล้วน
    result = (amount * _RATES[tier] * mult + 500) // 1000
    return min(result, _CAP)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("amount", "tier", "birthday"):
            if k not in data:
                raise ValueError("missing key: " + k)
        result = cashback(data["amount"], data["tier"], data["birthday"])
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
