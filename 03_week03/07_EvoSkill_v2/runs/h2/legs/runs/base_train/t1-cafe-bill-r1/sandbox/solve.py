"""BaanKafe — คำนวณยอดเงินที่ลูกค้าต้องจ่ายหน้าร้าน

ลำดับการคิดเงิน
1. ยอดรวม = ผลรวม(ราคาต่อชิ้น × จำนวน)  หน่วยเป็นสตางค์
2. ถ้ายอดรวม >= 500 บาท (50,000 สตางค์) ลด 5%
3. ถ้าเป็นสมาชิก (member=True) ลดอีก 10% จากยอดหลังขั้นที่ 2
4. บวก VAT 7% จากยอดสุดท้าย

การปัดเศษ: ปัดครึ่งขึ้น (ROUND_HALF_UP) ที่ระดับสตางค์ทุกขั้นตอน
เพื่อให้ตรงกับใบเสร็จที่แสดงเป็นสตางค์ และผลลัพธ์เป็นจำนวนเต็มสตางค์เสมอ
"""

from decimal import Decimal, ROUND_HALF_UP

BULK_THRESHOLD = 50_000  # 500 บาท ในหน่วยสตางค์
BULK_DISCOUNT = Decimal("0.05")
MEMBER_DISCOUNT = Decimal("0.10")
VAT_RATE = Decimal("0.07")


def _round_satang(amount: Decimal) -> int:
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์"""
    return int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย (จำนวนเต็มสตางค์)

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

    total = Decimal(subtotal)

    # ลด 5% เมื่อยอดรวมตั้งแต่ 500 บาทขึ้นไป
    if subtotal >= BULK_THRESHOLD:
        total = Decimal(_round_satang(total * (1 - BULK_DISCOUNT)))

    # สมาชิกลดอีก 10% จากยอดหลังลดขั้นแรก
    if member:
        total = Decimal(_round_satang(total * (1 - MEMBER_DISCOUNT)))

    # VAT 7% เป็นขั้นสุดท้าย
    total = Decimal(_round_satang(total * (1 + VAT_RATE)))

    return int(total)


if __name__ == "__main__":
    # ตัวอย่าง: กาแฟ 2 แก้ว ราคา 120 บาท (12,000 สตางค์) + เค้ก 1 ชิ้น 180 บาท
    sample = [
        {"price": 12_000, "qty": 2},
        {"price": 18_000, "qty": 1},
    ]
    print("ยอดรวมก่อนลด: 42000 สตางค์")
    print("ลูกค้าทั่วไป:", cafe_bill(sample, False), "สตางค์")
    print("สมาชิก:", cafe_bill(sample, True), "สตางค์")
