import json
import sys
from fractions import Fraction


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def cafe_bill(items, member):
    # สมมติฐาน: items ว่างถือเป็น input ผิด (ValueError); ราคา >= 0
    if type(items) is not list or not items:
        raise ValueError("items ต้องเป็น list ที่ไม่ว่าง")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True หรือ False")
    total = 0
    for it in items:
        if type(it) is not dict:
            raise ValueError("แต่ละรายการต้องเป็น dict")
        price = need_int(it.get("price"), "price", 0)
        qty = need_int(it.get("qty"), "qty", 1)
        total += price * qty
    amount = Fraction(total)
    if total >= 50000:  # 500 บาท
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)  # VAT ขั้นสุดท้าย ปัดครั้งเดียว
    return half_up(amount)


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
