import json
import sys

# อัตราเงินคืนเป็น basis points (1/10000)
RATES_BP = {"silver": 150, "gold": 250, "platinum": 400}
MIN_AMOUNT = 100 * 100   # 100 บาท เป็นสตางค์
MAX_CASHBACK = 200 * 100  # 200 บาท เป็นสตางค์


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative int (satang)")
    if not isinstance(tier, str) or tier not in RATES_BP:
        raise ValueError("tier must be 'silver', 'gold' or 'platinum'")
    if type(birthday) is not bool:
        raise ValueError("birthday must be a bool")

    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    # ปัดครึ่งขึ้นด้วยเลขจำนวนเต็มล้วน
    result = (amount * RATES_BP[tier] * mult + 5000) // 10000
    return min(result, MAX_CASHBACK)


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
