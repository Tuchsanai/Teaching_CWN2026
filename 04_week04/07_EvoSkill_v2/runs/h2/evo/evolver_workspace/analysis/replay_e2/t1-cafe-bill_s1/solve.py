"""ฟังก์ชันคิดเงินหน้าร้าน BaanKafe

กฎ (ทำตามลำดับ):
1. รวมยอดจาก items เป็นสตางค์ (จำนวนเต็ม)
2. ยอดรวมตั้งแต่ 500 บาท (50,000 สตางค์) ขึ้นไป ลด 5%
3. member = True ลดอีก 10% (คูณต่อจากยอดหลังข้อ 2)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. ปัดครั้งเดียวตอนท้าย เป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น เพราะเป็นเงินที่ลูกค้าจ่ายเข้าร้าน)

ไม่มี side effect ตอน import
"""

import math
from fractions import Fraction

THRESHOLD_SATANG = 50_000  # 500 บาท
BULK_DISCOUNT = Fraction(5, 100)
MEMBER_DISCOUNT = Fraction(10, 100)
VAT = Fraction(7, 100)


def _need_int(value, name, low=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    return value


def _need_bool(value, name):
    """flag: ต้องเป็น True หรือ False จริง"""
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


def _subtotal(items):
    """ตรวจ items ทั้งหมดก่อน แล้วคืนยอดรวมเป็นสตางค์ (จำนวนเต็ม)"""
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    total = 0
    for i, item in enumerate(items):
        if type(item) is not dict:
            raise ValueError(f"items[{i}] ต้องเป็น dict")
        if set(item.keys()) != {"price", "qty"}:
            raise ValueError(f"items[{i}] ต้องมีเฉพาะ key 'price' และ 'qty'")
        price = _need_int(item["price"], f"items[{i}].price", low=0)
        qty = _need_int(item["qty"], f"items[{i}].qty", low=1)
        total += price * qty
    return total


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย (จำนวนเต็มสตางค์)

    items: list ของ {"price": ราคาต่อชิ้นเป็นสตางค์ (int >= 0), "qty": จำนวนชิ้น (int >= 1)}
    member: True ถ้าเป็นสมาชิก (ลดเพิ่ม 10%)
    """
    _need_bool(member, "member")
    subtotal = _subtotal(items)

    # คำนวณเป็น Fraction ทั้งหมด ยังไม่ปัด
    total = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:
        total *= 1 - BULK_DISCOUNT
    if member:
        total *= 1 - MEMBER_DISCOUNT
    total *= 1 + VAT

    return _half_up(total)


if __name__ == "__main__":
    print(cafe_bill([{"price": 50_000, "qty": 1}], False))  # 50825
    print(cafe_bill([{"price": 50_000, "qty": 1}], True))   # 45743
