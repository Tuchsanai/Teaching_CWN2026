"""BaanKafe: คำนวณยอดเงินที่ลูกค้าต้องจ่ายหน้าร้าน

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม) เพื่อหลีกเลี่ยงปัญหาทศนิยมของ float
ลำดับการคิดเงิน:
    1. ยอดรวม = sum(price * qty)
    2. ยอดรวม >= 500 บาท (50000 สตางค์) -> ลด 5%
    3. เป็นสมาชิก (member=True)          -> ลดอีก 10% (จากยอดหลังขั้นที่ 2)
    4. บวก VAT 7% เป็นขั้นสุดท้าย
ทุกขั้นปัดเศษครึ่งขึ้น (half-up) ให้เหลือจำนวนเต็มสตางค์
"""

THRESHOLD_SATANG = 50000  # 500 บาท
THRESHOLD_DISCOUNT_PCT = 5
MEMBER_DISCOUNT_PCT = 10
VAT_PCT = 7


def _mul_div_half_up(value: int, numerator: int, denominator: int) -> int:
    """คำนวณ value * numerator / denominator แบบจำนวนเต็ม ปัดเศษครึ่งขึ้น.

    ใช้กับค่าที่ไม่ติดลบเท่านั้น (ราคาและยอดเงินในระบบไม่ติดลบ)
    """
    return (2 * value * numerator + denominator) // (2 * denominator)


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์.

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก
    """
    subtotal = 0
    for item in items:
        price = int(item["price"])
        qty = int(item["qty"])
        if price < 0:
            raise ValueError("price must not be negative")
        if qty < 1:
            raise ValueError("qty must be at least 1")
        subtotal += price * qty

    total = subtotal
    # ขั้นที่ 2: ลด 5% เมื่อยอดรวมตั้งแต่ 500 บาทขึ้นไป
    if subtotal >= THRESHOLD_SATANG:
        total = _mul_div_half_up(total, 100 - THRESHOLD_DISCOUNT_PCT, 100)

    # ขั้นที่ 3: สมาชิกลดอีก 10%
    if member:
        total = _mul_div_half_up(total, 100 - MEMBER_DISCOUNT_PCT, 100)

    # ขั้นที่ 4: บวก VAT 7% เป็นขั้นสุดท้าย
    total = _mul_div_half_up(total, 100 + VAT_PCT, 100)

    return total


if __name__ == "__main__":
    # ตัวอย่าง: ชา 200 บาท x 3 = 600 บาท
    sample = [{"price": 20000, "qty": 3}]
    print("สมาชิก:", cafe_bill(sample, True))      # 54891 สตางค์ = 548.91 บาท
    print("ไม่ใช่สมาชิก:", cafe_bill(sample, False))  # 60000*0.95*1.07 = 60990 สตางค์
