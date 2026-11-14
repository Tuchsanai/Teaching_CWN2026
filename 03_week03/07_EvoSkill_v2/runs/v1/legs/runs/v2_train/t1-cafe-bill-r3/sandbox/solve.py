import json
import sys
from fractions import Fraction


def need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def need_bool(v, name):
    if type(v) is not bool:
        raise ValueError(f"{name} ต้องเป็น True/False")
    return v


def cafe_bill(items, member):
    # สมมติฐาน: price >= 0, qty >= 1, list ว่าง = ยอด 0, ปัดครึ่งขึ้นครั้งเดียวตอนจบ (ลูกค้าจ่าย)
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    need_bool(member, "member")
    subtotal = 0
    for it in items:
        if type(it) is not dict:
            raise ValueError("item ต้องเป็น dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("item ต้องมี price และ qty")
        subtotal += need_int(it["price"], "price", 0) * need_int(it["qty"], "qty", 1)
    total = Fraction(subtotal)
    if subtotal >= 50000:
        total *= Fraction(95, 100)
    if member:
        total *= Fraction(90, 100)
    total *= Fraction(107, 100)
    return int((total * 2 + 1) // 2)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = cafe_bill(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
