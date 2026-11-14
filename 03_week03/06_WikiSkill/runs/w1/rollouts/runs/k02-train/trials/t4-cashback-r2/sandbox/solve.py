RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5% 2.5% 4%
MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
MAX_CASHBACK = 20000  # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่น้อยกว่า 0")
    if type(tier) is not str or tier not in RATES_PERMILLE:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น bool")

    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    # ปัดครั้งเดียว แบบครึ่งปัดขึ้น (ข้อสมมติ) ด้วยจำนวนเต็ม
    value = (amount * RATES_PERMILLE[tier] * mult + 500) // 1000
    return min(value, MAX_CASHBACK)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = cashback(**data)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)
