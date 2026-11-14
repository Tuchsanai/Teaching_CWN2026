"""BaanKafe: คิดเงินหน้าร้าน cafe_bill(items, member) — หน่วยสตางค์

นโยบาย: subtotal = Σ price×qty; ถ้า subtotal >= 50000 ลด 5%; member ลดอีก 10%;
VAT 7% เป็นขั้นสุดท้าย; ปัดครึ่งขึ้นครั้งเดียวตอนท้าย (ลูกค้าจ่าย) ด้วย Fraction
"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""
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
