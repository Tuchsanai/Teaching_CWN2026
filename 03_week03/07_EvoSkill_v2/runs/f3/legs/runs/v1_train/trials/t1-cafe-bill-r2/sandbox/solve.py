"""BaanKafe: cafe_bill (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    need_bool(member, "member")
    subtotal = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("item ต้องเป็น dict ที่มี price และ qty")
        subtotal += need_int(it["price"], "price", 0) * need_int(it["qty"], "qty", 1)
    x = Fraction(subtotal)
    if subtotal >= 50000:  # ตั้งแต่ 500 บาท ขึ้นไป (ก่อนลด) ลด 5%
        x *= Fraction(95, 100)
    if member:
        x *= Fraction(90, 100)
    x *= Fraction(107, 100)  # VAT ขั้นสุดท้าย
    return half_up(x)  # ปัดครั้งเดียวท้ายสุด


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
