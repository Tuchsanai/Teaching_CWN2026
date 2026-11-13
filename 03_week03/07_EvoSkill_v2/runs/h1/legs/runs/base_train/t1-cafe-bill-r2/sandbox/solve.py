"""BaanKafe: คำนวณยอดเงินที่ลูกค้าต้องจ่ายหน้าร้าน

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม) เพื่อหลีกเลี่ยงปัญหาทศนิยมของ float

ลำดับการคิดเงิน:
1. ยอดรวมก่อนลด = sum(price * qty)
2. ถ้ายอดรวมก่อนลด >= 500 บาท (50,000 สตางค์) ลด 5%
3. ถ้าเป็นสมาชิก (member=True) ลดอีก 10% (คิดต่อจากยอดหลังขั้นที่ 2)
4. บวก VAT 7% จากยอดหลังลด
5. ปัดผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น)
"""

from fractions import Fraction
from math import floor

THRESHOLD_SATANG = 50_000          # 500 บาท
BULK_DISCOUNT = Fraction(5, 100)   # 5%
MEMBER_DISCOUNT = Fraction(10, 100)  # 10%
VAT_RATE = Fraction(7, 100)        # 7%


def _validate_item(item):
    price = item["price"]
    qty = item["qty"]
    if isinstance(price, bool) or not isinstance(price, int) or price < 0:
        raise ValueError(f"price ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ: {price!r}")
    if isinstance(qty, bool) or not isinstance(qty, int) or qty < 1:
        raise ValueError(f"qty ต้องเป็นจำนวนเต็มตั้งแต่ 1: {qty!r}")


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น}
    member: True ถ้าเป็นสมาชิก (ลดเพิ่ม 10%)
    """
    for item in items:
        _validate_item(item)

    subtotal = sum(item["price"] * item["qty"] for item in items)  # สตางค์

    total = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:
        total *= 1 - BULK_DISCOUNT
    if member:
        total *= 1 - MEMBER_DISCOUNT
    total *= 1 + VAT_RATE

    # ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (ค่าไม่ติดลบเสมอ)
    return floor(total + Fraction(1, 2))


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    sample = [
        {"price": 4500, "qty": 2},   # 45 บาท x 2
        {"price": 6000, "qty": 5},   # 60 บาท x 5
    ]
    print("ยอดต้องจ่าย (ไม่เป็นสมาชิก):", cafe_bill(sample, False), "สตางค์")
    print("ยอดต้องจ่าย (สมาชิก):", cafe_bill(sample, True), "สตางค์")
