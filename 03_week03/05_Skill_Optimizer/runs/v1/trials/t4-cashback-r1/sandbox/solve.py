import json
import sys

# อัตราเงินคืนเป็นหน่วย 1/1000 (silver 1.5%, gold 2.5%, platinum 4%)
RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}
MIN_AMOUNT = 100 * 100   # 100 บาท (สตางค์)
MAX_CASHBACK = 200 * 100  # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative int")
    if type(tier) is not str or tier not in RATES_PERMILLE:
        raise ValueError("tier must be silver, gold or platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday must be a bool")
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES_PERMILLE[tier] * (2 if birthday else 1)
    # ปัดครึ่งขึ้นด้วยเลขจำนวนเต็มล้วน
    result = (amount * rate + 500) // 1000
    return min(result, MAX_CASHBACK)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("amount", "tier", "birthday"):
            if k not in data:
                raise ValueError("missing key: " + k)
        result = cashback(data["amount"], data["tier"], data["birthday"])
    except Exception as e:  # ทุกกรณีผิดพลาด
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
