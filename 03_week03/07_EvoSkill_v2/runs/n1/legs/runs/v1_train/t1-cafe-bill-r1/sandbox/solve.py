"""โครง solve.py สำหรับฟังก์ชันคิดเงิน (สตางค์) — แก้เฉพาะฟังก์ชันหลักด้านล่าง"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x >= 0) ใช้กับเงินที่ลูกค้าจ่าย"""
    return int((Fraction(x) * 2 + 1) // 2)


def round_down(x):
    """ปัดลง ใช้กับเงินที่ร้านจ่ายออก (cashback/rebate)"""
    return int(Fraction(x) // 1)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool, float, str ไม่ผ่าน
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
        raise ValueError(f"{name} ไม่อยู่ในรายการที่อนุญาต")
    return value


def cafe_bill(items, member):
    # สมมติฐาน: price >= 0 (0 รับได้), qty >= 1, items ว่างได้ -> 0 สตางค์
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    need_bool(member, "member")
    total = 0
    for item in items:
        if type(item) is not dict:
            raise ValueError("แต่ละรายการต้องเป็น dict")
        if "price" not in item or "qty" not in item:
            raise ValueError("รายการต้องมี price และ qty")
        total += need_int(item["price"], "price", 0) * need_int(item["qty"], "qty", 1)
    amount = Fraction(total)
    if total >= 50000:  # 500 บาท เทียบกับยอดรวมดิบ
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)  # VAT ขั้นสุดท้าย
    return half_up(amount)  # ปัดครึ่งขึ้นครั้งเดียว


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
