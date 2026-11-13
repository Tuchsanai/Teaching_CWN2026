"""BaanKafe: คำนวณยอดเงินที่ลูกค้าต้องจ่ายหน้าร้าน

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม) เพื่อไม่ให้เกิดปัญหาทศนิยมของ float
การปัดเศษใช้แบบ "ปัดขึ้นเมื่อ .5" (half-up) ทำด้วยจำนวนเต็มล้วน ๆ
และปัดหลังจากแต่ละขั้นตอน (ส่วนลด 5% -> ส่วนลดสมาชิก 10% -> VAT 7%)
"""


def _mul_div_half_up(value, numerator, denominator):
    """คืนค่า value * numerator / denominator ปัดแบบ half-up (value >= 0)."""
    return (2 * value * numerator + denominator) // (2 * denominator)


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    items: list ของ {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก (ลดเพิ่ม 10%)

    ขั้นตอน:
      1. รวมยอดสินค้า
      2. ถ้ายอดรวม >= 500 บาท (50000 สตางค์) ลด 5%
      3. ถ้าเป็นสมาชิก ลดอีก 10%
      4. บวก VAT 7% เป็นขั้นสุดท้าย
    """
    subtotal = 0
    for item in items:
        price = int(item["price"])
        qty = int(item["qty"])
        if price < 0:
            raise ValueError("price must be non-negative")
        if qty < 1:
            raise ValueError("qty must be at least 1")
        subtotal += price * qty

    total = subtotal

    # 500 บาท = 50000 สตางค์ ลด 5%
    if total >= 50000:
        total = _mul_div_half_up(total, 95, 100)

    # สมาชิกลดอีก 10%
    if member:
        total = _mul_div_half_up(total, 90, 100)

    # VAT 7% ขั้นสุดท้าย
    total = _mul_div_half_up(total, 107, 100)

    return total
