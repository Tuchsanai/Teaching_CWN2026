"""BaanKafe: คิดเงินหน้าร้าน

กฎ (เรียงตามลำดับที่โจทย์เขียน):
1. รวมยอดจาก price (สตางค์) * qty (ชิ้น) -> subtotal (สตางค์)
2. subtotal >= 50,000 สตางค์ (500 บาท) ลด 5%
3. member = True ลดอีก 10% (คูณต่อจากยอดหลังข้อ 2)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. ปัดครั้งเดียวตอนท้ายด้วยการปัดครึ่งขึ้น แล้วคืนจำนวนเต็มสตางค์

ไม่มี side effect ตอน import. ผิดชนิดหรือนอกช่วง -> ValueError เท่านั้น
"""

import math
from fractions import Fraction


# ---------- ตรวจข้อมูลนำเข้า ----------

def _need_int(value, name, low=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    return value


def _need_bool(value, name):
    """flag: ต้องเป็น True หรือ False จริง"""
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


# ---------- ปัดเศษ ----------

def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


# ---------- ฟังก์ชันหลัก ----------

def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย (จำนวนเต็มสตางค์)

    items:  list ของ dict {"price": ราคาต่อชิ้น (สตางค์, >= 0), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก (ลดเพิ่ม 10%)
    """
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    _need_bool(member, "member")

    subtotal = 0
    for i, item in enumerate(items):
        if type(item) is not dict:
            raise ValueError(f"items[{i}] ต้องเป็น dict")
        if "price" not in item or "qty" not in item:
            raise ValueError(f"items[{i}] ต้องมี key 'price' และ 'qty'")
        price = _need_int(item["price"], f"items[{i}].price", low=0)
        qty = _need_int(item["qty"], f"items[{i}].qty", low=1)
        subtotal += price * qty  # จำนวนเต็มล้วน ไม่ปัด

    total = Fraction(subtotal)

    # ข้อ 2: ยอดรวมตั้งแต่ 500 บาทขึ้นไป (50,000 สตางค์) ลด 5%
    if subtotal >= 50_000:
        total *= Fraction(95, 100)

    # ข้อ 3: สมาชิกลดอีก 10% จากยอดที่เหลือ
    if member:
        total *= Fraction(90, 100)

    # ข้อ 4: VAT 7% เป็นขั้นสุดท้าย
    total *= Fraction(107, 100)

    # ข้อ 5: ปัดครั้งเดียวตอนท้าย
    return _half_up(total)


if __name__ == "__main__":
    sample = [
        {"price": 6500, "qty": 2},  # 130 บาท
        {"price": 4500, "qty": 3},  # 135 บาท
        {"price": 3000, "qty": 4},  # 120 บาท  รวม 385 บาท (ยังไม่ถึง 500)
    ]
    print("ยอดที่ต้องจ่าย (สตางค์):", cafe_bill(sample, False))
    print("ยอดที่ต้องจ่าย (สมาชิก):", cafe_bill(sample, True))
