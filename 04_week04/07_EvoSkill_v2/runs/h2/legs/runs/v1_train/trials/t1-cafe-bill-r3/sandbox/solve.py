"""ฟังก์ชันคิดเงินหน้าร้าน BaanKafe

cafe_bill(items, member) -> จำนวนเต็มสตางค์ที่ลูกค้าต้องจ่าย

ลำดับการคิด (ปัดเศษครั้งเดียวตอนท้าย):
  1. รวมยอด = sum(price * qty) เป็นสตางค์ (จำนวนเต็ม)
  2. ถ้ายอดรวม >= 500 บาท (50,000 สตางค์) ลด 5%
  3. ถ้า member เป็น True ลดอีก 10% จากยอดที่เหลือ
  4. บวก VAT 7%
  5. ปัดครึ่งขึ้นเป็นสตางค์ทั้งหมด (เงินที่ลูกค้าจ่ายเข้าร้าน)

ไม่มี side effect ตอน import
"""
import math
from fractions import Fraction

SATANG_PER_BAHT = 100
BULK_THRESHOLD = 500 * SATANG_PER_BAHT  # ยอดรวมตั้งแต่ 500 บาทขึ้นไป (สตางค์)
BULK_DISCOUNT_PCT = 5
MEMBER_DISCOUNT_PCT = 10
VAT_PCT = 7


def _need_int(value, name, low=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์, int >= 0), "qty": จำนวนชิ้น (int >= 1)}
    member: True ถ้าเป็นสมาชิก (ลดอีก 10%)
    ค่าผิดชนิดหรือนอกช่วง -> ValueError
    """
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True หรือ False")

    subtotal = 0  # สตางค์ จำนวนเต็มทั้งหมด
    for i, item in enumerate(items):
        if type(item) is not dict:
            raise ValueError(f"items[{i}] ต้องเป็น dict")
        if "price" not in item or "qty" not in item:
            raise ValueError(f"items[{i}] ต้องมี key 'price' และ 'qty'")
        price = _need_int(item["price"], f"items[{i}].price", low=0)
        qty = _need_int(item["qty"], f"items[{i}].qty", low=1)
        subtotal += price * qty

    amount = Fraction(subtotal)
    if subtotal >= BULK_THRESHOLD:
        amount *= Fraction(100 - BULK_DISCOUNT_PCT, 100)
    if member:
        amount *= Fraction(100 - MEMBER_DISCOUNT_PCT, 100)
    amount *= Fraction(100 + VAT_PCT, 100)
    return _half_up(amount)


if __name__ == "__main__":
    # ตัวอย่าง: กาแฟ 2 แก้ว ราคา 65 บาท (สตางค์ 6500) + เค้ก 1 ชิ้น 120 บาท, ไม่ใช่สมาชิก
    sample = [{"price": 6500, "qty": 2}, {"price": 12000, "qty": 1}]
    print("ยอดรวม 250 บาท, ไม่ใช่สมาชิก:", cafe_bill(sample, False), "สตางค์")
