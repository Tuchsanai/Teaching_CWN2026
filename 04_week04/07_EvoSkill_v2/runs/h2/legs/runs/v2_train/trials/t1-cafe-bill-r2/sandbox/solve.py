"""BaanKafe: ฟังก์ชันคิดเงินหน้าร้าน

cafe_bill(items, member) -> จำนวนเงินที่ลูกค้าต้องจ่าย (สตางค์, จำนวนเต็ม)

กติกา (ทำตามลำดับนี้):
1. ยอดรวมก่อนลด = ผลรวม(price * qty) ทุกรายการ, หน่วยสตางค์
2. ยอดรวมตั้งแต่ 500 บาท (50000 สตางค์) ขึ้นไป ลด 5%
3. member = True ลดอีก 10% จากยอดที่เหลือ (คูณต่อเนื่อง ไม่ใช่บวกเป็น 15%)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. ปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียวตอนท้าย (ไม่ปัดระหว่างทาง)

ไม่มี side effect ตอน import
"""
import math
from fractions import Fraction

THRESHOLD_SATANG = 50000  # 500 บาท


# ---------- ตรวจข้อมูลนำเข้า (คัดลอกจาก skill strict-input-validation) ----------

def need_int(value, name, low=None, high=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


def need_bool(value, name):
    """flag: ต้องเป็น True หรือ False จริง"""
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


# ---------- ปัดเศษ (คัดลอกจาก skill money-arithmetic-rounding) ----------

def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


# ---------- ฟังก์ชันหลัก ----------

def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นสตางค์ (จำนวนเต็ม)

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์, >= 0), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก
    ผิดชนิดหรือนอกช่วง -> ValueError
    """
    if not isinstance(items, list):
        raise ValueError("items ต้องเป็น list")
    need_bool(member, "member")

    subtotal = 0
    for i, item in enumerate(items):
        if type(item) is not dict:
            raise ValueError(f"items[{i}] ต้องเป็น dict")
        if "price" not in item or "qty" not in item:
            raise ValueError(f"items[{i}] ต้องมีคีย์ price และ qty")
        price = need_int(item["price"], f"items[{i}].price", low=0)
        qty = need_int(item["qty"], f"items[{i}].qty", low=1)
        subtotal += price * qty

    total = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:          # ตั้งแต่ 500 บาทขึ้นไป (>=)
        total *= Fraction(95, 100)            # ลด 5%
    if member:
        total *= Fraction(90, 100)            # ลดอีก 10% จากยอดที่เหลือ
    total *= Fraction(107, 100)               # VAT 7% เป็นขั้นสุดท้าย
    return half_up(total)                     # ปัดครั้งเดียว


if __name__ == "__main__":
    example = [{"price": 12500, "qty": 3}, {"price": 9900, "qty": 2}]
    print(cafe_bill(example, True), "สตางค์")
