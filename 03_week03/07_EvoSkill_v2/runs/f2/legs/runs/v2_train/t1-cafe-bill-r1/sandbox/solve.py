"""BaanKafe: cafe_bill (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True หรือ False")
    subtotal = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("item ต้องเป็น dict ที่มี price และ qty")
        p, q = it["price"], it["qty"]
        if type(p) is not int or p < 0:
            raise ValueError("price ต้องเป็นจำนวนเต็ม >= 0")
        if type(q) is not int or q < 1:
            raise ValueError("qty ต้องเป็นจำนวนเต็ม >= 1")
        subtotal += p * q
    value = Fraction(subtotal)
    if subtotal >= 50000:  # 500 บาท
        value *= Fraction(95, 100)
    if member:
        value *= Fraction(90, 100)
    value *= Fraction(107, 100)  # VAT ขั้นสุดท้าย
    return half_up(value)  # ปัดครั้งเดียวท้ายสุด


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = cafe_bill(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
