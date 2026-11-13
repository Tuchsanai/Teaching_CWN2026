"""BaanKafe: คิดเงินหน้าร้าน (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


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


def cafe_bill(items, member):
    """คิดยอดสุทธิ: ลด 5% เมื่อรวม >= 500 บาท, สมาชิกลดอีก 10%, VAT 7% ปัดครึ่งขึ้นครั้งเดียว"""
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    need_bool(member, "member")
    subtotal = 0
    for item in items:
        if type(item) is not dict:
            raise ValueError("แต่ละรายการต้องเป็น dict")
        subtotal += need_int(item.get("price") if "price" in item else None, "price", 0) * need_int(item.get("qty") if "qty" in item else None, "qty", 1)
    amount = Fraction(subtotal)
    if subtotal >= 50000:          # "ตั้งแต่" = >=
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    return half_up(amount * Fraction(107, 100))   # ปัดครั้งเดียวตอนท้าย


# CLI (บังคับ): อ่าน JSON object จาก stdin -> พิมพ์ {"ok":..., "result"/"error":...}
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
