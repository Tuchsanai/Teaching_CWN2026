from fractions import Fraction

# อัตราเงินคืนเป็นเศษส่วนแท้ (ไม่ใช้ float)
RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
MIN_AMOUNT = 10000   # 100 บาท (สตางค์) ; พอดี 100 บาทได้เงินคืน
CAP = 20000          # 200 บาท (สตางค์) ต่อบิล


def cashback(amount, tier, birthday):
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่น้อยกว่า 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น bool")

    if amount < MIN_AMOUNT:
        return 0
    value = amount * RATES[tier]
    if birthday:
        value *= 2
    # ปัดครั้งเดียว (half up) แล้วจำกัดเพดาน
    result = int((value * 2 + 1) // 2)
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
