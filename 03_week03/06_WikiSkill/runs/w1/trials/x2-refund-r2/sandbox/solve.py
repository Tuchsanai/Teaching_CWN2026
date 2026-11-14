def _need_int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} ต้องไม่เกิน {hi}")


def refund(paid, used_percent, restock):
    _need_int("paid", paid, 0)
    _need_int("used_percent", used_percent, 0, 100)
    if type(restock) is not bool:
        raise ValueError("restock ต้องเป็น bool")
    if used_percent > 80:  # เกิน 80% ไม่คืน (พอดี 80% ยังคืน)
        return 0
    # สัดส่วนที่เหลือ x (หักค่าดำเนินการ 12.5% = x0.875) คำนวณด้วยจำนวนเต็ม ปัดครั้งเดียว
    # ปัดครึ่งขึ้น (half up)
    num = paid * (100 - used_percent) * (875 if restock else 1000)
    den = 100 * 1000
    return (2 * num + den) // (2 * den)


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
