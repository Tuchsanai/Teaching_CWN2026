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
    # 0.75% ต่อวัน (นับทุกวัน) สูงสุด 15% ; bp = basis points (1/10000)
    bp = min(75 * days_late, 1500)
    num = amount * bp
    # ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย (โจทย์ไม่ระบุวิธีปัด -> สมมติ half-up)
    return (2 * num + 10000) // 20000


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
