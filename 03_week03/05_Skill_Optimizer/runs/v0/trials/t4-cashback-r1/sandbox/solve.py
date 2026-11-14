import json
import sys

RATES_BPS = {"silver": 150, "gold": 250, "platinum": 400}  # หน่วย 1/10000
MIN_AMOUNT = 100_00   # 100 บาท (สตางค์)
MAX_CASHBACK = 200_00  # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("amount must be an integer (satang)")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not isinstance(tier, str) or tier not in RATES_BPS:
        raise ValueError("tier must be one of: silver, gold, platinum")
    if not isinstance(birthday, bool):
        raise ValueError("birthday must be a boolean")

    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    num = amount * RATES_BPS[tier] * mult
    result = (num + 5000) // 10000  # ปัดครึ่งขึ้น ด้วยเลขจำนวนเต็มล้วน
    return min(result, MAX_CASHBACK)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        raw = argv[0] if argv else sys.stdin.read()
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("amount", "tier", "birthday"):
            if k not in data:
                raise ValueError(f"missing field: {k}")
        out = {"cashback": cashback(data["amount"], data["tier"], data["birthday"])}
        print(json.dumps(out))
        return 0
    except (ValueError, TypeError) as e:
        print(json.dumps({"error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
