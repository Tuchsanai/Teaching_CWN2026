import json
import sys

_RATES = {"silver": 15, "gold": 25, "platinum": 40}  # ส่วน 1000
_DEN = 1000
_MIN_AMOUNT = 100 * 100   # 100 บาท (สตางค์)
_CAP = 200 * 100          # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative int")
    if type(tier) is not str or tier not in _RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")

    if amount < _MIN_AMOUNT:
        return 0
    mult = 2 if birthday and tier in ("gold", "platinum") else 1
    num = amount * _RATES[tier] * mult  # ตัวเศษ ตัวส่วน = 1000 (ค่าแม่นตรง)
    num = min(num, _CAP * _DEN)
    return num // _DEN  # เงินคืนปัดลงเสมอ


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("amount", "tier", "birthday"):
            if k not in data:
                raise ValueError("missing key: " + k)
        result = cashback(data["amount"], data["tier"], data["birthday"])
    except (ValueError, TypeError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
