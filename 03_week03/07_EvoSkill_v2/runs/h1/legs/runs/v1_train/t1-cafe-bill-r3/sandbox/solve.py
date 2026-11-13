"""BaanKafe: คำนวณยอดที่ลูกค้าต้องจ่ายหน้าร้าน

ลำดับการคิด (ทุกค่าเป็นสตางค์จำนวนเต็ม ปัดครั้งเดียวตอนท้าย):
1. ยอดรวม = ผลรวม price * qty ของทุกรายการ
2. ถ้ายอดรวม >= 50000 สตางค์ (500 บาท) ลด 5%
3. ถ้า member เป็น True ลดอีก 10% (คูณต่อจากข้อ 2)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์
"""

from fractions import Fraction

THRESHOLD_SATANG = 50000  # 500 บาท (ยอดรวมก่อนลดต้องถึงเกณฑ์นี้จึงได้ลด 5%)


def _require_int(value, label, lo=None):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม สำหรับ Fraction ที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True หรือ False")

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
        amount *= Fraction(95, 100)  # ลด 5%

    if member:
        amount *= Fraction(90, 100)  # ลดอีก 10% คูณต่อจากข้อก่อน

    amount *= Fraction(107, 100)  # VAT 7% เป็นขั้นสุดท้าย

    return _half_up(amount)


if __name__ == "__main__":
    # ตัวอย่างการใช้งานเล็ก ๆ (ไม่รันตอน import)
    print(cafe_bill([{"price": 10000, "qty": 3}], False))  # 32100
