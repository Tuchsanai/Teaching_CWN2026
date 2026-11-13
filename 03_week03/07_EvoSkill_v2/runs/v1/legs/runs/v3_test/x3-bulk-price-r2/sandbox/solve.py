"""BaanKafe: คิดราคาขายส่งเมล็ดกาแฟ (หน่วยสตางค์)"""
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
    """ตรวจว่าเป็น True/False จริง"""
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ต้องจ่าย (สตางค์) ปัดครึ่งขึ้นครั้งเดียวตอนท้าย"""
    need_int(unit_price, "unit_price", 0)
    need_int(qty, "qty", 1, 1000)
    need_bool(coupon, "coupon")
    amount = Fraction(unit_price * qty)
    if qty >= 50:
        amount *= Fraction(925, 1000)
    elif qty >= 10:
        amount *= Fraction(965, 1000)
    if coupon:
        amount *= Fraction(975, 1000)
    return half_up(amount * Fraction(107, 100))


def main():
    """CLI: อ่าน JSON จาก stdin"""
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
