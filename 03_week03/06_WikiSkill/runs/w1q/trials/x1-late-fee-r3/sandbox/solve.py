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
    # ค่าปรับ = amount * 0.75% * days (นับทุกวัน) สูงสุด 15% -> ใช้จำนวนเต็มล้วน
    # หน่วยเป็น 1/10000 ของสตางค์: 0.75% = 75, 15% = 1500
    num = min(amount * 75 * days_late, amount * 1500)
    # ข้อสมมติ: โจทย์ไม่ระบุการปัดเศษ -> ปัดครึ่งขึ้น (ปัดครั้งเดียวตอนท้าย)
    return (num * 2 + 10000) // 20000


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = late_fee(**data)
    except Exception as e:  # ValueError, TypeError, KeyError, JSONDecodeError
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)
