"""BaanKafe: cafe_bill — คิดเงินหน้าร้าน (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้น — เงินที่ลูกค้าจ่าย"""
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
    # มาตรฐานร้าน: ตรวจ input ครบก่อนคำนวณ; items ว่าง -> 0; price = 0 ผ่านได้
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    need_bool(member, "member")
    total = 0
    for it in items:
        if type(it) is not dict:
            raise ValueError("แต่ละรายการต้องเป็น dict")
        price = need_int(it.get("price"), "price", 0)
        qty = need_int(it.get("qty"), "qty", 1)
        total += price * qty

    amount = Fraction(total)
    if total >= 50000:  # ตั้งแต่ 500 บาท (ยอดรวมก่อนลด)
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)  # VAT ขั้นสุดท้าย
    return half_up(amount)  # ปัดครั้งเดียวตอนจบ


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
