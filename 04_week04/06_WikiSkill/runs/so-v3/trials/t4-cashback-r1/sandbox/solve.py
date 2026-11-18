import json
import sys

# อัตราเงินคืน (ตัวเศษ ส่วน 1000)
RATES = {"silver": 15, "gold": 25, "platinum": 40}
MIN_AMOUNT = 10000   # 100 บาท
CAP = 20000          # 200 บาท


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative int")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday and tier in ("gold", "platinum") else 1
    # เงินคืนเป็นเงินที่ร้านจ่ายออก: ปัดเศษลง
    value = amount * RATES[tier] * mult // 1000
    return min(value, CAP)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("amount", "tier", "birthday"):
            if k not in data:
                raise ValueError("missing key: " + k)
        result = cashback(data["amount"], data["tier"], data["birthday"])
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
