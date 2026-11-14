import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (ยอดที่ลูกค้าจ่าย)"""
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


def bulk_price(unit_price, qty, coupon):
    need_int(unit_price, "unit_price", 0)
    need_int(qty, "qty", 1, 1000)
    need_bool(coupon, "coupon")
    value = Fraction(unit_price) * qty
    # ส่วนลดปริมาณ ใช้อัตราเดียว (ไม่ซ้อน)
    if qty >= 50:
        value *= 1 - Fraction(75, 1000)
    elif qty >= 10:
        value *= 1 - Fraction(35, 1000)
    if coupon:
        value *= 1 - Fraction(25, 1000)
    value *= 1 + Fraction(7, 100)  # VAT ขั้นสุดท้าย
    return half_up(value)  # ปัดครั้งเดียวท้ายสุด


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
