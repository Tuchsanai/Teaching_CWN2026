"""BaanKafe: ราคาขายส่งเมล็ดกาแฟ (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้น — ใช้กับยอดที่ลูกค้าจ่าย"""
    return int((Fraction(x) * 2 + 1) // 2)


def bulk_price(unit_price, qty, coupon):
    if type(unit_price) is not int or unit_price < 0:
        raise ValueError("unit_price ต้องเป็นจำนวนเต็ม >= 0")
    if type(qty) is not int or qty < 1 or qty > 1000:
        raise ValueError("qty ต้องเป็นจำนวนเต็ม 1-1000")
    if type(coupon) is not bool:
        raise ValueError("coupon ต้องเป็น True หรือ False")

    total = Fraction(unit_price * qty)
    # ส่วนลดปริมาณ: อัตราเดียว (50+ -> 7.5%, 10+ -> 3.5%)
    if qty >= 50:
        total *= 1 - Fraction(75, 1000)
    elif qty >= 10:
        total *= 1 - Fraction(35, 1000)
    # คูปอง ลดอีก 2.5% (คูณต่อจากขั้นก่อน)
    if coupon:
        total *= 1 - Fraction(25, 1000)
    # VAT 7% ขั้นสุดท้าย แล้วปัดครั้งเดียว (half-up)
    total *= 1 + Fraction(7, 100)
    return half_up(total)


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
