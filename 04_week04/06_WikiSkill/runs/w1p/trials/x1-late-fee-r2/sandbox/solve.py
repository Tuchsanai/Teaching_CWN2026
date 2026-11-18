def _need_int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} ต้องไม่เกิน {hi}")


def late_fee(amount, days_late):
    _need_int("amount", amount, lo=0)
    _need_int("days_late", days_late, lo=0, hi=365)
    if days_late <= 3:
        return 0
    # 0.75% ต่อวัน = 75/10000 ; เพดาน 15% = 1500/10000 (คิดเป็นจำนวนเต็ม ปัดครึ่งขึ้นครั้งเดียว)
    num = amount * min(75 * days_late, 1500)
    return (num + 5000) // 10000


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = late_fee(**data)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)
