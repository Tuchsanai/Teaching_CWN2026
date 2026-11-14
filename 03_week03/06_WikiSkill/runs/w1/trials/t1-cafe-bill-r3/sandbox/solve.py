from fractions import Fraction

THRESHOLD = 50000  # 500 บาท = 50,000 สตางค์ (วัดจากยอดรวมก่อนลด)


def _need_int(name, v, lo=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {lo}")


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if not items:
        raise ValueError("items ต้องมีอย่างน้อย 1 รายการ")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น bool")
    total = 0
    for i, it in enumerate(items):
        if type(it) is not dict:
            raise ValueError(f"items[{i}] ต้องเป็น dict")
        if "price" not in it or "qty" not in it:
            raise ValueError(f"items[{i}] ต้องมี price และ qty")
        _need_int(f"items[{i}].price", it["price"], 0)
        _need_int(f"items[{i}].qty", it["qty"], 1)
        total += it["price"] * it["qty"]

    amount = Fraction(total)
    if total >= THRESHOLD:
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)
    # ปัดครั้งเดียวตอนท้าย แบบ half-up
    return int((amount * 2 + 1) // 2)


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
