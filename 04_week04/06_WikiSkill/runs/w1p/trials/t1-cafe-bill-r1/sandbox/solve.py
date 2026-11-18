def _need_int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} ต้องไม่เกิน {hi}")


def cafe_bill(items, member):
    if type(items) is not list or not items:
        raise ValueError("items ต้องเป็น list ที่ไม่ว่าง")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น bool")
    total = 0
    for it in items:
        if type(it) is not dict:
            raise ValueError("แต่ละรายการต้องเป็น dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("แต่ละรายการต้องมี price และ qty")
        _need_int("price", it["price"], lo=0)
        _need_int("qty", it["qty"], lo=1)
        total += it["price"] * it["qty"]

    # ใช้จำนวนเต็มล้วน: ส่วนลด/VAT เป็นเศษส่วน ปัดครั้งเดียวตอนท้าย (ครึ่งขึ้น)
    num, den = total, 1
    if total >= 50000:  # 500 บาท = 50,000 สตางค์ (พอดีเกณฑ์ได้ลด)
        num, den = num * 95, den * 100
    if member:  # ลดอีก 10% ต่อจากยอดหลังลดแล้ว
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100  # VAT 7% ขั้นสุดท้าย
    return (2 * num + den) // (2 * den)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = cafe_bill(**data)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)
