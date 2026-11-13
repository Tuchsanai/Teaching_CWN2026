"""BaanKafe: คำนวณยอดเงินที่ลูกค้าต้องจ่ายหน้าร้าน

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม) เพื่อหลีกเลี่ยงปัญหาทศนิยมของ float
ลำดับการคิดเงิน:
    1. ยอดรวม = sum(price * qty)
    2. ยอดรวม >= 500 บาท (50,000 สตางค์) -> ลด 5%
    3. ถ้าเป็นสมาชิก -> ลดอีก 10% (ลดต่อจากยอดหลังขั้นที่ 2)
    4. บวก VAT 7% เป็นขั้นสุดท้าย
ใช้ Fraction คำนวณแบบแม่นยำ และปัดเศษครั้งเดียวที่ท้ายสุด (ปัดขึ้นเมื่อครึ่งสตางค์)
"""

from fractions import Fraction
from decimal import Decimal, ROUND_HALF_UP

THRESHOLD_SATANG = 50_000  # 500 บาท
DISCOUNT_BULK = Fraction(5, 100)
DISCOUNT_MEMBER = Fraction(10, 100)
VAT_RATE = Fraction(7, 100)


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์

    items: list ของ dict {"price": ราคาต่อชิ้นเป็นสตางค์, "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก
    """
    subtotal = 0
    for item in items:
        price = item["price"]
        qty = item["qty"]
        if not isinstance(price, int) or price < 0:
            raise ValueError(f"price ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ: {price!r}")
        if not isinstance(qty, int) or qty < 1:
            raise ValueError(f"qty ต้องเป็นจำนวนเต็มตั้งแต่ 1: {qty!r}")
        subtotal += price * qty

    total = Fraction(subtotal)

    # ขั้นที่ 2: ลด 5% เมื่อยอดรวมตั้งแต่ 500 บาทขึ้นไป
    if subtotal >= THRESHOLD_SATANG:
        total *= 1 - DISCOUNT_BULK

    # ขั้นที่ 3: สมาชิกลดอีก 10%
    if member:
        total *= 1 - DISCOUNT_MEMBER

    # ขั้นที่ 4: VAT 7% เป็นขั้นสุดท้าย
    total *= 1 + VAT_RATE

    # ปัดเป็นจำนวนเต็มสตางค์ (ครึ่งสตางค์ปัดขึ้น)
    amount = Decimal(total.numerator) / Decimal(total.denominator)
    return int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


if __name__ == "__main__":
    # ตัวอย่าง: ลาเต้ 300 บาท x 2 = 600 บาท -> ลด 5% -> สมาชิกลด 10% -> VAT 7%
    sample = [{"price": 30_000, "qty": 2}]
    print(cafe_bill(sample, member=True))   # 54891 สตางค์ = 548.91 บาท
    print(cafe_bill(sample, member=False))  # 60000 * 0.95 * 1.07 = 60990 สตางค์
    print(cafe_bill([{"price": 20_000, "qty": 2}], member=False))  # 40000 < 50000 -> 42800
