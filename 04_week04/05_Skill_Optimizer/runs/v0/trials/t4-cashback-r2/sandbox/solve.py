"""BaanKafe cashback. เงินทุกค่าเป็นจำนวนเต็มสตางค์ ไม่ใช้ float"""
import json
import sys

RATES_BP = {"silver": 150, "gold": 250, "platinum": 400}  # หน่วย 1/10000
MIN_AMOUNT = 100 * 100   # 100 บาท
MAX_CASHBACK = 200 * 100  # 200 บาท


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount must be an integer (satang)")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not isinstance(tier, str) or tier not in RATES_BP:
        raise ValueError("tier must be one of: silver, gold, platinum")
    if not isinstance(birthday, bool):
        raise TypeError("birthday must be a boolean")

    if amount < MIN_AMOUNT:
        return 0
    num = amount * RATES_BP[tier] * (2 if birthday else 1)
    # ปัดครึ่งขึ้นเป็นสตางค์ด้วยจำนวนเต็มล้วน
    result = (2 * num + 10000) // 20000
    return min(result, MAX_CASHBACK)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        raw = argv[0] if argv else sys.stdin.read()
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        missing = [k for k in ("amount", "tier", "birthday") if k not in data]
        if missing:
            raise ValueError("missing fields: " + ", ".join(missing))
        out = {"cashback": cashback(data["amount"], data["tier"], data["birthday"])}
        print(json.dumps(out))
        return 0
    except (ValueError, TypeError) as e:  # รวม JSONDecodeError
        print(json.dumps({"error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
