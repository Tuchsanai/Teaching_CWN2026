import json
import sys

# อัตราเงินคืนเป็นเศษส่วนจำนวนเต็ม (ตัวเศษ, ตัวส่วน)
RATES = {"silver": (15, 1000), "gold": (25, 1000), "platinum": (40, 1000)}
MIN_AMOUNT = 100 * 100   # 100 บาท เป็นสตางค์
CAP = 200 * 100          # 200 บาท เป็นสตางค์
BIRTHDAY_TIERS = ("gold", "platinum")


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative int")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < MIN_AMOUNT:
        return 0
    num, den = RATES[tier]
    if birthday and tier in BIRTHDAY_TIERS:
        num *= 2
    # เทียบเพดานด้วยค่าแม่นตรง: amount*num/den > CAP
    if amount * num >= CAP * den:
        return CAP
    # เงินคืนเป็นเงินที่ร้านจ่ายออก ปัดเศษลงเสมอ
    return (amount * num) // den


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
