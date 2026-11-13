"""BaanKafe: คิดยอดที่ลูกค้าต้องจ่าย หน่วยเป็นสตางค์ (int)

ลำดับการคิด:
1. รวมยอด subtotal จาก price × qty (สตางค์)
2. ถ้า subtotal >= 50000 สตางค์ (500 บาทขึ้นไป) ลด 5%
3. ถ้า member เป็น True ลดอีก 10% (คูณต่อจากยอดหลังข้อ 2)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. คำนวณด้วย Fraction ทั้งหมด แล้วปัดครึ่งขึ้นครั้งเดียวตอนท้าย
"""
import json
import sys
from fractions import Fraction

THRESHOLD_SATANG = 50_000  # 500 บาท (ตั้งแต่ขึ้นไป = รวมขอบ)
BULK_DISCOUNT = Fraction(5, 100)
MEMBER_DISCOUNT = Fraction(10, 100)
VAT = Fraction(7, 100)


def _require_int(value, label, lo=None):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    return value


def _require_flag(value, label):
    if type(value) is not bool:
        raise ValueError(f"{label} ต้องเป็น True หรือ False")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม รับ Fraction ที่ไม่ติดลบ"""
    return int((x * 2 + 1) // 2)


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    items: list ของ dict {"price": ราคาต่อชิ้นเป็นสตางค์, "qty": จำนวนชิ้น >= 1}
    member: True ถ้าเป็นสมาชิก
    """
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    _require_flag(member, "member")

    subtotal = 0
    for i, item in enumerate(items):
        if type(item) is not dict:
            raise ValueError(f"items[{i}] ต้องเป็น dict")
        if "price" not in item or "qty" not in item:
            raise ValueError(f"items[{i}] ต้องมี price และ qty")
        price = _require_int(item["price"], f"items[{i}].price", lo=0)
        qty = _require_int(item["qty"], f"items[{i}].qty", lo=1)
        subtotal += price * qty

    amount = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:
        amount *= 1 - BULK_DISCOUNT
    if member:
        amount *= 1 - MEMBER_DISCOUNT
    amount *= 1 + VAT
    return _half_up(amount)


def main():
    try:
        args = json.load(sys.stdin)
        if type(args) is not dict:
            raise ValueError("input ต้องเป็น JSON object")
        result = cafe_bill(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
