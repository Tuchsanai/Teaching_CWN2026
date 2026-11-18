def _need_int(name, v, lo=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {lo}")


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น bool")
    total = 0
    for it in items:
        if type(it) is not dict:
            raise ValueError("แต่ละรายการต้องเป็น dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("แต่ละรายการต้องมี price และ qty")
        _need_int("price", it["price"], 0)
        _need_int("qty", it["qty"], 1)
        total += it["price"] * it["qty"]

    # ใช้เลขจำนวนเต็มล้วน: ตัวเศษ/ตัวส่วน แล้วปัดครึ่งขึ้นครั้งเดียวตอนท้าย
    num, den = total, 1
    if total >= 50000:          # 500 บาท พอดีก็ลด 5%
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
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
