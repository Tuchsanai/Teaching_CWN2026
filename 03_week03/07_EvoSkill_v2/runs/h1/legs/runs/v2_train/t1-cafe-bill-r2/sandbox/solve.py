"""BaanKafe: คิดเงินหน้าร้าน

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม)
ลำดับการคิด:
  1. รวมยอด = Σ price × qty
  2. ยอดรวม >= 50,000 สตางค์ (500 บาท) ลด 5%  (× 95/100)
  3. member = True ลดอีก 10%                 (× 90/100), คูณต่อจากข้อ 2
  4. บวก VAT 7% เป็นขั้นสุดท้าย                (× 107/100)
  5. ปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียวตอนท้าย (คำนวณด้วย Fraction ไม่มี float)
"""

import json
import sys
from fractions import Fraction

THRESHOLD_SATANG = 50_000  # 500 บาท
DISCOUNT_THRESHOLD_RATE = Fraction(95, 100)  # ลด 5%
MEMBER_RATE = Fraction(90, 100)              # ลดอีก 10%
VAT_RATE = Fraction(107, 100)                # VAT 7%


def _validate_items(items):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    for index, item in enumerate(items):
        label = f"items[{index}]"
        if type(item) is not dict:
            raise ValueError(f"{label} ต้องเป็น dict")
        if "price" not in item or "qty" not in item:
            raise ValueError(f"{label} ต้องมี field price และ qty")
        price = item["price"]
        qty = item["qty"]
        if type(price) is not int:
            raise ValueError(f"{label}.price ต้องเป็นจำนวนเต็มสตางค์")
        if price < 0:
            raise ValueError(f"{label}.price ต้องไม่ติดลบ")
        if type(qty) is not int:
            raise ValueError(f"{label}.qty ต้องเป็นจำนวนเต็ม")
        if qty < 1:
            raise ValueError(f"{label}.qty ต้องไม่น้อยกว่า 1")


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์"""
    _validate_items(items)
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True หรือ False")

    subtotal = sum(item["price"] * item["qty"] for item in items)

    amount = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:
        amount *= DISCOUNT_THRESHOLD_RATE
    if member:
        amount *= MEMBER_RATE
    amount *= VAT_RATE

    # ปัดครึ่งขึ้นครั้งเดียว (amount >= 0 เสมอ)
    return int((amount * 2 + 1) // 2)


def main():
    try:
        args = json.load(sys.stdin)
        if type(args) is not dict:
            raise ValueError("input ต้องเป็น JSON object")
        result = cafe_bill(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
