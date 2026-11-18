"""BaanKafe: คิดเงินหน้าร้าน

cafe_bill(items, member) -> จำนวนเต็มสตางค์ที่ลูกค้าต้องจ่าย

กฎ (ตามลำดับ):
1. ยอดรวม S = ผลรวม price * qty (สตางค์, จำนวนเต็ม)
2. ถ้า S >= 50000 สตางค์ (500 บาทขึ้นไป) ลด 5%
3. ถ้า member เป็น True ลดอีก 10% (คูณต่อจากยอดหลังข้อ 2)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. ปัดครั้งเดียวตอนท้าย แบบปัดครึ่งขึ้น (เงินที่ลูกค้าจ่ายเข้าร้าน)

ไม่ใช้ float ในการคำนวณเงิน ใช้ Fraction ทั้งหมด
ผิดชนิดหรือนอกช่วง -> ValueError เท่านั้น
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
    """คืนยอดที่ลูกค้าต้องจ่าย (สตางค์, จำนวนเต็ม)

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์, >= 0), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก (ลด 10% เพิ่ม)
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
        price = _need_int(item["price"], f"items[{i}]['price']", low=0)
        qty = _need_int(item["qty"], f"items[{i}]['qty']", low=1)
        subtotal += price * qty

    # ยังไม่ปัดระหว่างทาง ใช้ Fraction ทั้งหมด
    amount = Fraction(subtotal)
    if subtotal >= 50000:                 # ตั้งแต่ 500 บาทขึ้นไป
        amount *= Fraction(95, 100)       # ลด 5%
    if member:
        amount *= Fraction(90, 100)       # สมาชิกลดอีก 10%
    amount *= Fraction(107, 100)          # VAT 7% ขั้นสุดท้าย

    return _half_up(amount)               # ปัดครั้งเดียวตอนท้าย


if __name__ == "__main__":
    demo = [{"price": 20000, "qty": 3}]   # 600 บาท
    print("ยอดที่ต้องจ่าย (สตางค์):", cafe_bill(demo, False))
    print("สมาชิก (สตางค์):", cafe_bill(demo, True))
