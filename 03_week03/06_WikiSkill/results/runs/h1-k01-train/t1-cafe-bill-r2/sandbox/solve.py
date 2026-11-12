"""BaanKafe cashier bill calculator.

หน่วยทั้งหมดเป็นสตางค์ (1 บาท = 100 สตางค์) และคำนวณด้วยจำนวนเต็มล้วน
การปัดเศษ ใช้ "ปัดขึ้นเมื่อครึ่งหนึ่งพอดี" (round half up) ทุกขั้นที่เป็นเงิน
"""

THRESHOLD_SATANG = 500 * 100  # 500 บาท
BULK_DISCOUNT_NUM, BULK_DISCOUNT_DEN = 95, 100  # ลด 5%  -> คูณ 95/100
MEMBER_DISCOUNT_NUM, MEMBER_DISCOUNT_DEN = 90, 100  # ลดเพิ่ม 10% -> คูณ 90/100
VAT_NUM, VAT_DEN = 107, 100  # VAT 7% -> คูณ 107/100


def _mul_div_round(value: int, num: int, den: int) -> int:
    """คำนวณ value * num / den แล้วปัดครึ่งขึ้น (value >= 0, den > 0)."""
    return (value * num * 2 + den) // (den * 2)


def cafe_bill(items, member: bool) -> int:
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นสตางค์ (จำนวนเต็ม)

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก (ลดเพิ่ม 10%)
    """
    subtotal = 0
    for item in items:
        subtotal += int(item["price"]) * int(item["qty"])

    total = subtotal
    # ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5% (เทียบกับยอดก่อนลดสมาชิก)
    if total >= THRESHOLD_SATANG:
        total = _mul_div_round(total, BULK_DISCOUNT_NUM, BULK_DISCOUNT_DEN)

    # สมาชิกลดเพิ่ม 10%
    if member:
        total = _mul_div_round(total, MEMBER_DISCOUNT_NUM, MEMBER_DISCOUNT_DEN)

    # VAT 7% เป็นขั้นสุดท้าย
    total = _mul_div_round(total, VAT_NUM, VAT_DEN)
    return total


if __name__ == "__main__":
    # ตัวอย่าง: กาแฟ 65 บาท x 8 แก้ว = 520 บาท (ถึงเกณฑ์ลด 5%), เป็นสมาชิก
    sample = [{"price": 6500, "qty": 8}]
    print(cafe_bill(sample, member=True))
