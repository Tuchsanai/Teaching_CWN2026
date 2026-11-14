"""BaanKafe: bulk_price(unit_price, qty, coupon) -> ยอดที่ลูกค้าต้องจ่าย (สตางค์, จำนวนเต็ม)

กติกา
1. unit_price = ราคาต่อถุงเป็นสตางค์ (int, ตั้งแต่ 0)
2. qty        = จำนวนถุง (int, 1–1000)
3. coupon     = True คือมีคูปอง (bool)
4. ส่วนลดขั้นบันไดตาม qty ใช้อัตราเดียว ไม่สะสม:
   - qty >= 50  -> ลด 7.5%
   - qty >= 10  -> ลด 3.5%
   - อื่น ๆ      -> ไม่ลด
5. coupon = True -> ลดอีก 2.5% คิดต่อจากยอดหลังลดขั้นบันได (ทบต้น)
6. VAT 7% คิดจากยอดหลังลดทั้งหมด เป็นขั้นสุดท้าย
7. คำนวณทั้งสายด้วย Fraction แล้วปัดครึ่งขึ้นครั้งเดียวตอนท้าย
"""
import json
import sys
from fractions import Fraction
from math import floor


def _need_int(value, name, low=None, high=None):
    # bool เป็น subclass ของ int จึงต้องเช็กด้วย type() ตรง ๆ
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def _need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ)"""
    return floor(Fraction(x) + Fraction(1, 2))


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์"""
    try:
        _need_int(unit_price, "unit_price", low=0)
        _need_int(qty, "qty", low=1, high=1000)
        _need_bool(coupon, "coupon")

        if qty >= 50:
            bulk_rate = Fraction(75, 1000)  # 7.5%
        elif qty >= 10:
            bulk_rate = Fraction(35, 1000)  # 3.5%
        else:
            bulk_rate = Fraction(0)

        total = Fraction(unit_price) * qty
        total *= 1 - bulk_rate
        if coupon:
            total *= 1 - Fraction(25, 1000)  # คูปอง 2.5% ทบต้น
        total *= Fraction(107, 100)  # VAT 7% ขั้นสุดท้าย

        return _half_up(total)
    except ValueError:
        raise
    except (TypeError, ZeroDivisionError, KeyError, ArithmeticError) as exc:
        raise ValueError(f"ข้อมูลไม่ถูกต้อง: {exc}") from exc


def main():
    try:
        args = json.loads(sys.stdin.read())
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = bulk_price(**args)
    except (ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
