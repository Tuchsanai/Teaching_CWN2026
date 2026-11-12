import json
import sys

# อัตราเงินคืน เป็นเศษส่วนของ 1000 (หลีกเลี่ยง float)
RATES_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}
MIN_AMOUNT = 10_000   # 100 บาท (สตางค์)
MAX_CASHBACK = 20_000  # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    """คืนเงินคืนเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น ปัดครั้งเดียวหลังคูณสองเท่า แล้วจึงจำกัดเพดาน)"""
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("amount must be an integer (satang)")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not isinstance(tier, str) or tier not in RATES_PER_MILLE:
        raise ValueError("tier must be one of: silver, gold, platinum")
    if not isinstance(birthday, bool):
        raise ValueError("birthday must be a boolean")

    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    num = amount * RATES_PER_MILLE[tier] * mult
    result = (num + 500) // 1000  # round half up, จำนวนเต็มล้วน
    return min(result, MAX_CASHBACK)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        missing = [k for k in ("amount", "tier", "birthday") if k not in data]
        if missing:
            raise ValueError("missing field(s): " + ", ".join(missing))
        out = {"cashback": cashback(data["amount"], data["tier"], data["birthday"])}
        print(json.dumps(out))
        return 0
    except (ValueError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
