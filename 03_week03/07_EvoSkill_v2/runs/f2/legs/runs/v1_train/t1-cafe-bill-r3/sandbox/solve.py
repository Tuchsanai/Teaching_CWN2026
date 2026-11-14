"""BaanKafe: cafe_bill(items, member) -> สตางค์ที่ลูกค้าต้องจ่าย"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้น (ยอดที่ลูกค้าจ่าย)"""
    return int((Fraction(x) * 2 + 1) // 2)


def cafe_bill(items, member):
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True หรือ False")
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    subtotal = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("item ต้องเป็น dict ที่มี price และ qty")
        price, qty = it["price"], it["qty"]
        if type(price) is not int or price < 0:
            raise ValueError("price ต้องเป็นจำนวนเต็มตั้งแต่ 0")
        if type(qty) is not int or qty < 1:
            raise ValueError("qty ต้องเป็นจำนวนเต็มตั้งแต่ 1")
        subtotal += price * qty

    value = Fraction(subtotal)
    if subtotal >= 50000:  # 500 บาท = 50000 สตางค์
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
