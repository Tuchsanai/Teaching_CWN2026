"""แม่แบบ solve.py — คัดลอกทั้งไฟล์ แก้ชื่อ/ตัวฟังก์ชัน example ตาม brief แล้วแก้ `FUNC` ใน main() ให้เป็นฟังก์ชันจริง"""
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


# ตัวอย่างรูปแบบ (แก้ตาม brief) -------------------------------------------
def example(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    need_bool(member, "member")
    subtotal = 0
    for item in items:
        if type(item) is not dict:
            raise ValueError("แต่ละรายการต้องเป็น dict")
        subtotal += need_int(item.get("price"), "price", 0) * need_int(item.get("qty"), "qty", 1)
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
        result = example(**args)  # เปลี่ยน example เป็นชื่อฟังก์ชันจริง (FUNC)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
