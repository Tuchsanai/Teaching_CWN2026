def _need_int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} ต้องไม่เกิน {hi}")


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if not items:
        raise ValueError("items ต้องไม่ว่าง")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น bool")
    total = 0
    for i, it in enumerate(items):
        if type(it) is not dict:
            raise ValueError(f"items[{i}] ต้องเป็น dict")
        if "price" not in it or "qty" not in it:
            raise ValueError(f"items[{i}] ต้องมี price และ qty")
        _need_int(f"items[{i}].price", it["price"], lo=0)
        _need_int(f"items[{i}].qty", it["qty"], lo=1)
        total += it["price"] * it["qty"]

    # ทำงานเป็นเศษส่วน num/den ปัดครั้งเดียวตอนท้าย (half up)
    num, den = total, 1
    if total >= 50000:          # ตั้งแต่ 500 บาท (พอดีก็ลด)
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
    except Exception as e:  # ValueError, TypeError, KeyError, JSONDecodeError
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)
