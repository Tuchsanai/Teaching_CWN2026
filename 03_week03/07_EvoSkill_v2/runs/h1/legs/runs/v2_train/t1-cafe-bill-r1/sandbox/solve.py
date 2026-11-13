"""คิดเงินหน้าร้าน BaanKafe

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม)

ลำดับการคิด:
1. รวมยอดจาก price * qty ทุกรายการ
2. ยอดรวม >= 50000 สตางค์ (500 บาท) ลด 5%
3. member = True ลดอีก 10% (คูณต่อจากข้อ 2)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. คำนวณด้วย Fraction ไม่ปัดระหว่างทาง แล้วปัดครึ่งขึ้นครั้งเดียวตอนท้าย
"""

import json
import sys
from fractions import Fraction

DISCOUNT_THRESHOLD = 50000  # 500 บาท เป็นสตางค์


def _require_int(value, label, minimum):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if value < minimum:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {minimum}")
    return value


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True หรือ False")

    subtotal = 0
    for index, item in enumerate(items):
        if type(item) is not dict:
            raise ValueError(f"รายการที่ {index} ต้องเป็น dict")
        if "price" not in item or "qty" not in item:
            raise ValueError(f"รายการที่ {index} ต้องมี price และ qty")
        price = _require_int(item["price"], f"price ของรายการที่ {index}", 0)
        qty = _require_int(item["qty"], f"qty ของรายการที่ {index}", 1)
        subtotal += price * qty

    amount = Fraction(subtotal)
    if subtotal >= DISCOUNT_THRESHOLD:
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)

    # ปัดครึ่งขึ้นครั้งเดียว (amount ไม่ติดลบเสมอ)
    return int((amount * 2 + 1) // 2)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = cafe_bill(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
