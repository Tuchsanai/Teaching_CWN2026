"""BaanKafe: คิดราคาขายส่งเมล็ดกาแฟ

กฎ:
1. ซื้อ 50 ถุงขึ้นไป ลด 7.5%, ซื้อ 10 ถุงขึ้นไป ลด 3.5% (ใช้อัตราเดียว ไม่สะสม)
2. มีคูปอง ลดอีก 2.5% (คูณต่อจากยอดที่เหลือ)
3. บวก VAT 7% เป็นขั้นสุดท้าย
4. ปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียวตอนท้าย (ยอดที่ลูกค้าจ่ายเข้าร้าน)

หน่วย: unit_price เป็นสตางค์ ผลลัพธ์เป็นสตางค์ (จำนวนเต็ม)
"""
import math
from fractions import Fraction


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


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


def bulk_discount_rate(qty):
    """อัตราส่วนลดขายส่ง (อัตราเดียว ตามเกณฑ์สูงสุดที่ถึง)"""
    if qty >= 50:
        return Fraction(75, 1000)  # 7.5%
    if qty >= 10:
        return Fraction(35, 1000)  # 3.5%
    return Fraction(0)


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่าย (สตางค์, จำนวนเต็ม)

    unit_price: ราคาต่อถุง (สตางค์, ตั้งแต่ 0)
    qty: จำนวนถุง (1–1000)
    coupon: True ถ้ามีคูปอง
    """
    # ตรวจ input ทุกตัวก่อนคำนวณ
    need_int(unit_price, "unit_price", low=0)
    need_int(qty, "qty", low=1, high=1000)
    need_bool(coupon, "coupon")

    # คำนวณแบบ exact ทุกขั้น ยังไม่ปัด
    total = Fraction(unit_price * qty)
    total *= 1 - bulk_discount_rate(qty)
    if coupon:
        total *= 1 - Fraction(25, 1000)  # คูปอง 2.5%
    total *= 1 + Fraction(7, 100)  # VAT 7% (ขั้นสุดท้าย)

    # ปัดครั้งเดียวตอนท้าย
    return half_up(total)


if __name__ == "__main__":
    print(bulk_price(10000, 10, False))  # 103255
    print(bulk_price(10000, 50, True))   # 482503
