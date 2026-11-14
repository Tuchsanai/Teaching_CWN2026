"""BaanKafe: คิดเงินหน้าร้าน

ลำดับการคิด (ทำตามโจทย์ทุกข้อ):
1. ยอดรวม = sum(price * qty)                         (หน่วยสตางค์, จำนวนเต็ม)
2. ถ้ายอดรวม >= 50000 สตางค์ (500 บาท) ลด 5%         (เทียบกับยอดก่อนลดทุกข้อ)
3. ถ้า member = True ลดอีก 10%                       (คิดต่อเนื่องจากยอดหลังข้อ 2)
4. บวก VAT 7% เป็นขั้นสุดท้าย                         (คูณ 1.07 บนยอดหลังส่วนลดทั้งหมด)
5. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ ครั้งเดียวที่ขั้นสุดท้าย

การตีความที่เลือก (กำกวม):
- "ลดอีก 10%" อ่านเป็นลดต่อเนื่อง (x * 0.95 * 0.90) ไม่ใช่รวมเป็น 15%
- เกณฑ์ 500 บาทตรวจจากยอดก่อนหักส่วนลดของสมาชิก
- การปัดเศษ: ครึ่งขึ้น (ROUND_HALF_UP) ที่ขั้นสุดท้ายเท่านั้น
"""

from fractions import Fraction
import math

THRESHOLD_SATANG = 50_000      # 500 บาท
DISCOUNT_BULK_PCT = 5          # ลด 5% เมื่อถึงเกณฑ์
DISCOUNT_MEMBER_PCT = 10       # ลดอีก 10% สำหรับสมาชิก
VAT_PCT = 7


def _round_half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ค่าไม่ติดลบ)."""
    return math.floor(Fraction(x) + Fraction(1, 2))


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์.

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก
    """
    subtotal = 0
    for item in items:
        price = int(item["price"])
        qty = int(item["qty"])
        if price < 0:
            raise ValueError("price ต้องไม่ติดลบ")
        if qty < 1:
            raise ValueError("qty ต้องมีค่าตั้งแต่ 1 ขึ้นไป")
        subtotal += price * qty

    amount = Fraction(subtotal)

    # ขั้น 2: ลด 5% เมื่อยอดก่อนลดตั้งแต่ 500 บาทขึ้นไป
    if subtotal >= THRESHOLD_SATANG:
        amount *= Fraction(100 - DISCOUNT_BULK_PCT, 100)

    # ขั้น 3: สมาชิกลดอีก 10% (ต่อเนื่องจากข้อ 2)
    if member:
        amount *= Fraction(100 - DISCOUNT_MEMBER_PCT, 100)

    # ขั้น 4: VAT 7% เป็นขั้นสุดท้าย
    amount *= Fraction(100 + VAT_PCT, 100)

    # ขั้น 5: ปัดครั้งเดียว
    return _round_half_up(amount)


if __name__ == "__main__":
    sample = [{"price": 15000, "qty": 2}, {"price": 25000, "qty": 2}]
    print(cafe_bill(sample, member=True))
