"""BaanKafe: คิดเงินหน้าร้าน (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None, high=None):
    """ตรวจว่าเป็น int จริง (ไม่รับ bool/float) และอยู่ในช่วง"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    """ตรวจว่าเป็น bool จริง"""
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def cafe_bill(items, member):
    """คิดยอดจ่ายสุทธิ (สตางค์): ลด 5% เมื่อยอด >= 500 บาท, สมาชิกลด 10%, บวก VAT 7%"""
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    need_bool(member, "member")
    subtotal = 0
    for item in items:
        if type(item) is not dict:
            raise ValueError("แต่ละรายการต้องเป็น dict")
        if "price" not in item or "qty" not in item:
            raise ValueError("รายการต้องมี price และ qty")
        subtotal += need_int(item["price"], "price", 0) * need_int(item["qty"], "qty", 1)
    amount = Fraction(subtotal)
    if subtotal >= 50000:
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    return half_up(amount * Fraction(107, 100))


def main():
    """CLI: อ่าน JSON จาก stdin"""
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
