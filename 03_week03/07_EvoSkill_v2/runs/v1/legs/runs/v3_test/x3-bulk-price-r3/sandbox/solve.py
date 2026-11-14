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
    """ยอดที่ลูกค้าจ่าย (สตางค์).

    สมมติฐาน: ปัดครึ่งขึ้นครั้งเดียวตอนจบ (เงินที่ลูกค้าจ่าย);
    ส่วนลดปริมาณใช้อัตราเดียว (>=50 ได้ 7.5% ไม่ซ้อนกับ 3.5%);
    ส่วนลดคูณต่อกัน แล้วบวก VAT เป็นขั้นสุดท้าย
    """
    need_int(unit_price, "unit_price", low=0)
    need_int(qty, "qty", low=1, high=1000)
    need_bool(coupon, "coupon")

    total = Fraction(unit_price * qty)
    if qty >= 50:
        total *= Fraction(1000 - 75, 1000)
    elif qty >= 10:
        total *= Fraction(1000 - 35, 1000)
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
