import json
import sys
from fractions import Fraction


def need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def need_bool(v, name):
    if type(v) is not bool:
        raise ValueError(f"{name} ต้องเป็น True/False")
    return v


def bulk_price(unit_price, qty, coupon):
    """ราคาขายส่ง (สตางค์). สมมติฐาน: ส่วนลดคูณต่อกัน (ลดตามจำนวน แล้วลดคูปองอีก)
    VAT เป็นขั้นสุดท้าย ปัดครึ่งขึ้นครั้งเดียวตอนจบ (ลูกค้าเป็นผู้จ่าย)"""
    need_int(unit_price, "unit_price", 0)
    need_int(qty, "qty", 1, 1000)
    need_bool(coupon, "coupon")

    total = Fraction(unit_price * qty)
    if qty >= 50:
        total *= Fraction(925, 1000)
    elif qty >= 10:
        total *= Fraction(965, 1000)
    if coupon:
        total *= Fraction(975, 1000)
    total *= Fraction(107, 100)
    return int((total * 2 + 1) // 2)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = bulk_price(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
