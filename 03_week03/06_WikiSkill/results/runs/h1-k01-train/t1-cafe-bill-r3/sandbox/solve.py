"""BaanKafe cashier bill calculator.

ราคาทุกค่าเป็นสตางค์ (จำนวนเต็ม) ผลลัพธ์ก็เป็นสตางค์ (จำนวนเต็ม)

ลำดับการคิดเงิน:
1. ยอดรวมก่อนลด = sum(price * qty)
2. ถ้ายอดรวมก่อนลด >= 500 บาท (50,000 สตางค์) ลด 5%
3. ถ้าเป็นสมาชิก (member=True) ลดอีก 10% จากยอดหลังขั้นที่ 2
4. บวก VAT 7% จากยอดหลังขั้นที่ 3 (ขั้นสุดท้าย)

แต่ละขั้นปัดเศษเป็นสตางค์แบบ ROUND_HALF_UP และใช้ Decimal เพื่อหลีกเลี่ยงความคลาดเคลื่อนของ float
"""

from decimal import Decimal, ROUND_HALF_UP

THRESHOLD_SATANG = 50_000  # 500 บาท
BULK_DISCOUNT = Decimal("0.05")
MEMBER_DISCOUNT = Decimal("0.10")
VAT_RATE = Decimal("0.07")


def _apply(amount: int, factor: Decimal) -> int:
    """คูณยอดด้วย factor แล้วปัดเศษเป็นสตางค์ (จำนวนเต็ม)."""
    result = (Decimal(amount) * factor).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(result)


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นสตางค์ (จำนวนเต็ม).

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก
    """
    subtotal = 0
    for item in items:
        price = int(item["price"])
        qty = int(item["qty"])
        if price < 0 or qty < 1:
            raise ValueError("price must be >= 0 and qty must be >= 1")
        subtotal += price * qty

    total = subtotal

    # ขั้นที่ 1: ลด 5% เมื่อยอดรวมตั้งแต่ 500 บาทขึ้นไป
    if subtotal >= THRESHOLD_SATANG:
        total = _apply(total, Decimal("1") - BULK_DISCOUNT)

    # ขั้นที่ 2: สมาชิกลดอีก 10%
    if member:
        total = _apply(total, Decimal("1") - MEMBER_DISCOUNT)

    # ขั้นที่ 3: บวก VAT 7% (ขั้นสุดท้าย)
    total = _apply(total, Decimal("1") + VAT_RATE)

    return total


if __name__ == "__main__":
    sample = [
        {"price": 4500, "qty": 2},   # 90 บาท
        {"price": 6000, "qty": 5},   # 300 บาท
        {"price": 12000, "qty": 2},  # 240 บาท  -> รวม 630 บาท
    ]
    print("ไม่ใช่สมาชิก:", cafe_bill(sample, member=False))
    print("สมาชิก:", cafe_bill(sample, member=True))
