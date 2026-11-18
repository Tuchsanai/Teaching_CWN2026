RATES = {"silver": (15, 1000), "gold": (25, 1000), "platinum": (4, 100)}
MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
CAP = 20000          # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่น้อยกว่า 0")
    if not (type(tier) is str and tier in RATES):
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น bool")

    if amount < MIN_AMOUNT:
        return 0
    num, den = RATES[tier]
    mult = 2 if birthday and tier in ("gold", "platinum") else 1
    result = amount * num * mult // den  # ปัดลง
    return min(result, CAP)


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
