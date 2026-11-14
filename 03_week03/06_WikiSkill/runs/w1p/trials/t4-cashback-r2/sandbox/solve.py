RATES = {"silver": 15, "gold": 25, "platinum": 40}  # หน่วยต่อ 1000 (1.5%, 2.5%, 4%)
DOUBLE_TIERS = {"gold", "platinum"}  # นโยบายร้าน: เดือนเกิดได้ 2 เท่าเฉพาะ gold/platinum
MIN_AMOUNT = 10000  # 100 บาท (สตางค์)
MAX_CASHBACK = 20000  # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่น้อยกว่า 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday and tier in DOUBLE_TIERS else 1
    result = amount * RATES[tier] * mult // 1000  # ปัดลงครั้งเดียว
    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = cashback(**data)
    except Exception as e:  # ValueError, TypeError, KeyError, JSONDecodeError
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)
