"""BaanKafe cashback calculator. Money is in satang (int), no decimals."""
import json
import sys

# อัตราเงินคืนเป็นเศษส่วนจำนวนเต็ม ตัวส่วน 1000 (1.5% = 15/1000)
RATE_NUM = {"silver": 15, "gold": 25, "platinum": 40}
RATE_DEN = 1000
MIN_AMOUNT = 10000          # 100 บาท
MAX_CASHBACK = 20000        # 200 บาทต่อบิล
BIRTHDAY_MULTIPLIER = 2
REQUIRED = ("amount", "tier", "birthday")


def cashback(amount, tier, birthday):
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if type(tier) is not str or tier not in RATE_NUM:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น true หรือ false")
    if amount < MIN_AMOUNT:
        return 0
    mult = BIRTHDAY_MULTIPLIER if birthday else 1
    num = amount * RATE_NUM[tier] * mult
    den = RATE_DEN
    # ปัดครั้งเดียวที่ขั้นสุดท้าย แบบครึ่งปัดขึ้น (half-up)
    result = (2 * num + den) // (2 * den)
    return min(result, MAX_CASHBACK)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input ต้องเป็น JSON object")
        missing = [k for k in REQUIRED if k not in data]
        if missing:
            raise ValueError("ขาด key: " + ", ".join(missing))
        unknown = [k for k in data if k not in REQUIRED]
        if unknown:
            raise ValueError("key ไม่รู้จัก: " + ", ".join(unknown))
        result = cashback(**{k: data[k] for k in REQUIRED})
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
