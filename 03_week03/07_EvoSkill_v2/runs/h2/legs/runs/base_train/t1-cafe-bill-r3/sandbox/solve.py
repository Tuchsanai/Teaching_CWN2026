"""BaanKafe - คำนวณยอดเงินที่ลูกค้าต้องจ่ายหน้าร้าน

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม) เพื่อหลีกเลี่ยงปัญหาทศนิยมของ float

ลำดับการคิด:
1. ยอดรวม = ผลรวม(ราคาต่อชิ้น * จำนวนชิ้น)
2. ถ้ายอดรวม >= 500 บาท (50,000 สตางค์) ลด 5%
3. ถ้าเป็นสมาชิก (member=True) ลดอีก 10% จากยอดหลังขั้นที่ 2 (ลดต่อเนื่อง ไม่ใช่รวมเป็น 15%)
4. บวก VAT 7% จากยอดหลังส่วนลดทั้งหมด (ขั้นสุดท้าย)

การปัดเศษ: ทุกขั้นปัดครึ่งขึ้น (ROUND_HALF_UP) ให้เป็นจำนวนเต็มสตางค์
"""

THRESHOLD_SATANG = 50_000  # 500 บาท


def _round_half_up_percent(amount: int, percent: int) -> int:
    """คืนค่า amount * percent / 100 ปัดครึ่งขึ้นเป็นจำนวนเต็ม (amount >= 0)."""
    return (amount * percent + 50) // 100


def cafe_bill(items, member: bool) -> int:
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์.

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
            raise ValueError("qty ต้องมีอย่างน้อย 1")
        subtotal += price * qty

    total = subtotal
    if total >= THRESHOLD_SATANG:
        total = _round_half_up_percent(total, 95)  # ลด 5%

    if member:
        total = _round_half_up_percent(total, 90)  # ลดอีก 10%

    total = _round_half_up_percent(total, 107)  # บวก VAT 7%
    return total


if __name__ == "__main__":
    sample = [
        {"price": 4500, "qty": 2},   # 90 บาท x 2
        {"price": 12000, "qty": 3},  # 120 บาท x 3 -> รวม 450 บาท
    ]
    print(cafe_bill(sample, member=False))  # ยอดรวม 45,000 สต. (ไม่ถึง 500 บาท ไม่ลด) -> VAT 7% = 48,150
    print(cafe_bill(sample, member=True))   # 45,000 -> ลด 10% = 40,500 -> VAT 7% = 43,335
