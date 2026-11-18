"""เทมเพลต solve.py สำหรับโจทย์คิดเงิน (คัดลอกแล้วแก้ฟังก์ชันหลัก)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ) — ใช้กับเงินที่ลูกค้าจ่าย"""
    return int((Fraction(x) * 2 + 1) // 2)


def round_down(x):
    """ปัดลง (x ไม่ติดลบ) — ใช้กับเงินที่ร้านจ่ายออก เช่น เงินคืน"""
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
        raise ValueError(f"{name} ต้องเป็นหนึ่งใน {sorted(choices)}")
    return value


def bulk_price(unit_price, qty, coupon):
    need_int(unit_price, "unit_price", 0)
    need_int(qty, "qty", 1, 1000)
    need_bool(coupon, "coupon")
    x = Fraction(unit_price) * qty
    if qty >= 50:
        x *= Fraction(1000 - 75, 1000)
    elif qty >= 10:
        x *= Fraction(1000 - 35, 1000)
    if coupon:
        x *= Fraction(1000 - 25, 1000)
    x *= Fraction(107, 100)
    return half_up(x)


def main():
    """อ่าน JSON object จาก stdin → เรียกฟังก์ชัน → พิมพ์ผล (เผื่อถูกเรียกผ่าน CLI)"""
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = bulk_price(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
