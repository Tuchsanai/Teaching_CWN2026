"""BaanKafe: คิดราคาขายส่งเมล็ดกาแฟ (หน่วยสตางค์)

นโยบาย:
- ส่วนลดตามจำนวน: >=10 ถุง ลด 3.5%, >=50 ถุง ลด 7.5% (ใช้อัตราเดียว ไม่ทบกัน)
- คูปอง ลดอีก 2.5% (คูณทบต่อจากส่วนลดจำนวน)
- VAT 7% เป็นขั้นสุดท้าย
- ใช้ Fraction ตลอด ปัดครึ่งขึ้น (ลูกค้าจ่ายร้าน) ครั้งเดียวตอนท้าย
"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ) — ใช้กับเงินที่ลูกค้าจ่าย"""
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


def bulk_price(unit_price, qty, coupon):
    need_int(unit_price, "unit_price", 0)
    need_int(qty, "qty", 1, 1000)
    need_bool(coupon, "coupon")
    x = Fraction(unit_price) * qty
    if qty >= 50:
        x *= Fraction(1000 - 75, 1000)   # ลด 7.5%
    elif qty >= 10:
        x *= Fraction(1000 - 35, 1000)   # ลด 3.5%
    if coupon:
        x *= Fraction(1000 - 25, 1000)   # คูปองลดอีก 2.5% (คูณทบ)
    x *= Fraction(107, 100)              # VAT สุดท้าย
    return half_up(x)


def main():
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
