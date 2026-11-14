"""BaanKafe: คิดเงินหน้าร้าน

กฎ (ทุกค่าเป็นสตางค์ เป็นจำนวนเต็ม):
1. ยอดรวม = sum(price * qty)
2. ถ้ายอดรวม >= 50,000 สตางค์ (500 บาท) ลด 5%
3. ถ้า member เป็น True ลดอีก 10% (คิดต่อจากยอดหลังข้อ 2)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. ปัดเศษครั้งเดียวตอนท้ายสุดแบบปัดครึ่งขึ้น (half-up) คืนเป็น int สตางค์
"""

from fractions import Fraction

THRESHOLD_SATANG = 50_000  # 500 บาท
DISCOUNT_BULK = Fraction(5, 100)
DISCOUNT_MEMBER = Fraction(10, 100)
VAT = Fraction(7, 100)


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int, x ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def _require_int(value, name, low=None):
    if type(value) is not int:  # ปฏิเสธ bool, float, str, None
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    return value


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย (สตางค์, int)

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์, int >= 0), "qty": จำนวนชิ้น (int >= 1)}
    member: True/False
    """
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True หรือ False")

    # ตรวจ input ทั้งหมดก่อนคำนวณ
    subtotal = 0
    for entry in items:
        if type(entry) is not dict:
            raise ValueError("แต่ละรายการใน items ต้องเป็น dict")
        price = _require_int(entry.get("price"), "price", low=0)
        qty = _require_int(entry.get("qty"), "qty", low=1)
        subtotal += price * qty

    # คำนวณทั้งหมดด้วย Fraction ยังไม่ปัด
    total = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:
        total -= total * DISCOUNT_BULK
    if member:
        total -= total * DISCOUNT_MEMBER
    total += total * VAT

    # ปัดครั้งเดียว
    return _half_up(total)


if __name__ == "__main__":
    print(cafe_bill([{"price": 15000, "qty": 4}], False))
