"""BaanKafe: คิดเงินหน้าร้าน cafe_bill(items, member)

กติกา (ทั้งหมดคิดเป็นสตางค์):
1. ยอดรวมก่อนลด = sum(price * qty) ของทุกรายการ
2. ยอดรวมก่อนลดตั้งแต่ 500 บาท (50000 สตางค์) ขึ้นไป ลด 5%
3. member = True ลดอีก 10% คิดต่อจากยอดหลังข้อ 2 (ทบต้น ไม่ใช่บวกเปอร์เซ็นต์รวมกัน)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. คำนวณด้วย Fraction ตลอดทาง ปัดครึ่งขึ้นครั้งเดียวตอนท้ายสุด
"""
import json
import sys
from fractions import Fraction
from math import floor

THRESHOLD_SATANG = 50000  # 500 บาท


def _need_int(value, name, low=None):
    # type(...) is int เพื่อ reject bool และ float (เช่น 4500.0)
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ)"""
    return floor(Fraction(x) + Fraction(1, 2))


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"""
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True หรือ False")

    subtotal = 0  # สตางค์ (int ล้วน)
    for i, item in enumerate(items):
        if type(item) is not dict:
            raise ValueError(f"รายการที่ {i} ต้องเป็น dict")
        if "price" not in item or "qty" not in item:
            raise ValueError(f"รายการที่ {i} ต้องมี key price และ qty")
        price = _need_int(item["price"], f"price ของรายการที่ {i}", low=0)
        qty = _need_int(item["qty"], f"qty ของรายการที่ {i}", low=1)
        subtotal += price * qty

    total = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:
        total *= Fraction(95, 100)
    if member:
        total *= Fraction(90, 100)
    total *= Fraction(107, 100)
    return _half_up(total)


def main():
    try:
        args = json.loads(sys.stdin.read())
        if type(args) is not dict:
            raise ValueError("input ต้องเป็น JSON object")
        result = cafe_bill(**args)
    except (ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
