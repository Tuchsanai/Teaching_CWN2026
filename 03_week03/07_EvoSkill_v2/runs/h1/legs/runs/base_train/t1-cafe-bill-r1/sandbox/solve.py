from decimal import Decimal, ROUND_HALF_UP

# หน่วยทั้งหมดเป็นสตางค์ (1 บาท = 100 สตางค์)
BULK_THRESHOLD = 500 * 100  # ยอดรวมตั้งแต่ 500 บาทขึ้นไป
BULK_DISCOUNT = Decimal("0.05")  # ลด 5%
MEMBER_DISCOUNT = Decimal("0.10")  # ลดอีก 10% สำหรับสมาชิก
VAT_RATE = Decimal("0.07")  # VAT 7% (บวกเป็นขั้นสุดท้าย)


def cafe_bill(items, member):
    """คำนวณยอดที่ลูกค้าต้องจ่าย (สตางค์, จำนวนเต็ม)

    items: list ของ {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก
    """
    # 1) ยอดรวมก่อนลด (จำนวนเต็มสตางค์)
    subtotal = sum(int(item["price"]) * int(item["qty"]) for item in items)

    total = Decimal(subtotal)

    # 2) ลด 5% เมื่อยอดรวมตั้งแต่ 500 บาทขึ้นไป (เทียบกับยอดก่อนลด)
    if subtotal >= BULK_THRESHOLD:
        total *= 1 - BULK_DISCOUNT

    # 3) สมาชิกลดอีก 10% (ลดต่อจากขั้นที่ 2)
    if member:
        total *= 1 - MEMBER_DISCOUNT

    # 4) บวก VAT 7% เป็นขั้นสุดท้าย
    total *= 1 + VAT_RATE

    # 5) ปัดเป็นสตางค์จำนวนเต็ม (ปัดครึ่งขึ้น)
    return int(total.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


if __name__ == "__main__":
    # ตัวอย่าง: ยอดรวม 600 บาท, ไม่ใช่สมาชิก -> 600 * 0.95 * 1.07 = 609.90 บาท
    sample = [{"price": 15000, "qty": 4}]  # 150 บาท x 4 = 600 บาท
    print(cafe_bill(sample, False))  # 60990
    print(cafe_bill(sample, True))   # 600 * 0.95 * 0.90 * 1.07 = 548.91 บาท -> 54891
    print(cafe_bill([{"price": 4500, "qty": 2}], True))  # 90 บาท, ไม่ถึง 500 -> 90 * 0.90 * 1.07 = 86.67 บาท -> 8667
