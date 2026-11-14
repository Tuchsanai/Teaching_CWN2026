RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5% 2.5% 4%
MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
MAX_CASHBACK = 20000  # 200 บาท (สตางค์)


def _need_int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} ต้องไม่เกิน {hi}")


def cashback(amount, tier, birthday):
    _need_int("amount", amount, lo=0)
    if type(tier) is not str or tier not in RATES_PERMILLE:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น bool")

    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    num = amount * RATES_PERMILLE[tier] * mult  # หารด้วย 1000
    result = (2 * num + 1000) // 2000  # ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย
    return min(result, MAX_CASHBACK)


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
