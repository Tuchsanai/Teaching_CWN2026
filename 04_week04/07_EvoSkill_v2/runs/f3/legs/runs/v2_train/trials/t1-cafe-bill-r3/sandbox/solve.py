"""solve.py — cafe_bill ของ BaanKafe (เงินเป็นสตางค์จำนวนเต็ม)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ) — ใช้กับเงินที่ลูกค้าจ่าย"""
    return int((Fraction(x) * 2 + 1) // 2)


def round_down(x):
    """ปัดลง — ใช้กับเงินที่ร้านจ่ายออก เช่น เงินคืน"""
    return int(Fraction(x) // 1)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool และ float ไม่ใช่ int
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def need_choice(value, name, choices):
    if type(value) is not str or value not in choices:
        raise ValueError(f"{name} ต้องเป็นหนึ่งใน {list(choices)}")
    return value


def cafe_bill(items, member):
    """คิดเงินหน้าร้าน (สตางค์): ยอดรวม ≥ 50000 ลด 5%, member ลดอีก 10%, VAT 7% ท้ายสุด
    เงื่อนไขขั้นต่ำอิงยอดก่อนลด; ปัดครึ่งขึ้นครั้งเดียวตอนท้าย (ลูกค้าจ่าย); list ว่าง = 0"""
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    need_bool(member, "member")
    subtotal = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("แต่ละรายการต้องเป็น dict ที่มี price และ qty")
        subtotal += need_int(it["price"], "price", 0) * need_int(it["qty"], "qty", 1)
    x = Fraction(subtotal)
    if subtotal >= 50000:
        x *= Fraction(95, 100)
    if member:
        x *= Fraction(90, 100)
    x *= Fraction(107, 100)
    return half_up(x)


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
