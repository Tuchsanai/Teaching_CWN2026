from fractions import Fraction


def _need_int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} ต้องไม่เกิน {hi}")


def refund(paid, used_percent, restock):
    _need_int("paid", paid, lo=0)
    _need_int("used_percent", used_percent, lo=0, hi=100)
    if type(restock) is not bool:
        raise ValueError("restock ต้องเป็น bool")
    if used_percent > 80:
        return 0
    amount = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amount *= Fraction(7, 8)  # หักค่าดำเนินการ 12.5%
    # ปัดครั้งเดียวตอนท้าย แบบ half-up
    return int((amount * 2 + 1) // 2)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = refund(**data)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)
