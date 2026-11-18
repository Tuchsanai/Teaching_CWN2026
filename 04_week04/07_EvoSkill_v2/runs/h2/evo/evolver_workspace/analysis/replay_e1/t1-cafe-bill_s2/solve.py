"""BaanKafe: คิดเงินหน้าร้าน cafe_bill(items, member)

กติกา (ตามลำดับ):
  1. ยอดรวมก่อนลด = sum(price * qty) เป็นสตางค์
  2. ยอดรวมตั้งแต่ 500 บาท (50,000 สตางค์) ขึ้นไป -> ลด 5%
  3. member = True -> ลดอีก 10% (คูณต่อจากยอดหลังข้อ 2)
  4. บวก VAT 7% เป็นขั้นสุดท้าย
  5. ปัดครั้งเดียวตอนท้าย (ปัดครึ่งขึ้น เพราะเป็นเงินที่ลูกค้าจ่ายเข้าร้าน)
     คืนจำนวนเต็มสตางค์

ไม่มี side effect ตอน import.
"""

import math
from fractions import Fraction


# ---------- ตรวจข้อมูลนำเข้า (ผิดอะไรก็ตาม -> ValueError) ----------

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


# ---------- ปัดเศษ ----------

def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


# ---------- ฟังก์ชันหลัก ----------

DISCOUNT_THRESHOLD = 50_000  # 500 บาท เป็นสตางค์


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย (จำนวนเต็มสตางค์)

    items: list ของ dict {"price": ราคาต่อชิ้นเป็นสตางค์ (int >= 0),
                          "qty": จำนวนชิ้น (int >= 1)}
    member: True/False
    """
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    need_bool(member, "member")

    subtotal = 0
    for i, item in enumerate(items):
        if type(item) is not dict:
            raise ValueError(f"items[{i}] ต้องเป็น dict")
        if "price" not in item or "qty" not in item:
            raise ValueError(f"items[{i}] ต้องมี key 'price' และ 'qty'")
        price = need_int(item["price"], f"items[{i}]['price']", low=0)
        qty = need_int(item["qty"], f"items[{i}]['qty']", low=1)
        subtotal += price * qty

    # คำนวณทั้งหมดแบบ exact ด้วย Fraction ยังไม่ปัด
    total = Fraction(subtotal)
    if subtotal >= DISCOUNT_THRESHOLD:
        total *= Fraction(95, 100)          # ลด 5%
    if member:
        total *= Fraction(90, 100)          # ลดอีก 10% (คูณต่อ)
    total *= Fraction(107, 100)             # VAT 7% ขั้นสุดท้าย

    # ปัดครั้งเดียวตอนท้าย
    return half_up(total)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน: 3 ชิ้นราคา 200 บาท (20,000 สตางค์) เป็นสมาชิก
    sample = [{"price": 20000, "qty": 3}]
    print(cafe_bill(sample, True))
