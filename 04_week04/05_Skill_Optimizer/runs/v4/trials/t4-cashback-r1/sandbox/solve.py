import json
import sys

RATES_BP = {"silver": 150, "gold": 250, "platinum": 400}  # หน่วย 1/10000
MIN_AMOUNT = 10000   # 100 บาท
CAP = 20000          # 200 บาท
BIRTHDAY_TIERS = {"gold", "platinum"}  # นโยบายร้าน: 2 เท่าเฉพาะ gold/platinum


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative int (satang)")
    if type(tier) is not str or tier not in RATES_BP:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday and tier in BIRTHDAY_TIERS else 1
    # คำนวณแบบจำนวนเต็ม ปัดเศษลงครั้งเดียวตอนท้าย
    return min(amount * RATES_BP[tier] * mult // 10000, CAP)


def main():
    try:
        d = json.load(sys.stdin)
        out = {"cashback": cashback(d["amount"], d["tier"], d["birthday"])}
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({"error": str(e)}))
        return 1
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
