import json
import sys

RATES_BP = {"silver": 150, "gold": 250, "platinum": 400}  # หน่วย 1/10000
BIRTHDAY_TIERS = {"gold", "platinum"}  # นโยบาย: 2 เท่าเฉพาะ gold/platinum
MIN_AMOUNT = 10000   # 100 บาท
CAP = 20000          # 200 บาท


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
    # คำนวณเป็นจำนวนเต็ม ปัดเศษลงครั้งเดียวตอนท้าย
    result = amount * RATES_BP[tier] * mult // 10000
    return min(result, CAP)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        out = {"cashback": cashback(data.get("amount"), data.get("tier"),
                                    data.get("birthday"))}
    except (ValueError, TypeError) as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
