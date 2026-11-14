"""BaanKafe: bulk_price (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def bulk_price(unit_price, qty, coupon):
    if type(unit_price) is not int or unit_price < 0:
        raise ValueError("unit_price ต้องเป็นจำนวนเต็ม >= 0")
    if type(qty) is not int or not (1 <= qty <= 1000):
        raise ValueError("qty ต้องเป็นจำนวนเต็ม 1-1000")
    if type(coupon) is not bool:
        raise ValueError("coupon ต้องเป็น bool")
    total = Fraction(unit_price * qty)
    if qty >= 50:
        total *= 1 - Fraction(75, 1000)   # ใช้อัตราเดียว (ไม่ซ้อน)
    elif qty >= 10:
        total *= 1 - Fraction(35, 1000)
    if coupon:
        total *= 1 - Fraction(25, 1000)   # คูณต่อจากส่วนลดก่อนหน้า
    total *= Fraction(107, 100)           # VAT ขั้นสุดท้าย
    return half_up(total)                 # ปัดครั้งเดียว half-up


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = bulk_price(**args)
    except (ValueError, TypeError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
