"""คิดราคาขายส่งเมล็ดกาแฟ BaanKafe

หน่วยทั้งหมดเป็นสตางค์ ใช้ Fraction ตลอดการคำนวณ และปัดครั้งเดียวที่ขั้นสุดท้าย
ลำดับการคิด:
  1. ยอดตั้งต้น = unit_price * qty
  2. ลดตามจำนวนถุง: >=50 ถุง ลด 7.5%, >=10 ถุง ลด 3.5% (ใช้อัตราเดียว)
  3. ถ้ามีคูปอง ลดอีก 2.5% บนยอดที่เหลือหลังขั้นที่ 2 (ต่อเนื่อง ไม่ใช่รวมเปอร์เซ็นต์)
  4. บวก VAT 7% เป็นขั้นสุดท้าย
  5. ปัดครึ่งเข้าเลขคู่ (round-half-even) เป็นจำนวนเต็มสตางค์
"""

from fractions import Fraction

BULK_TIER_50 = Fraction(75, 1000)   # 7.5% สำหรับ 50 ถุงขึ้นไป
BULK_TIER_10 = Fraction(35, 1000)   # 3.5% สำหรับ 10 ถุงขึ้นไป
COUPON_RATE = Fraction(25, 1000)    # 2.5% คูปอง (ลดต่อจากขั้นขายส่ง)
VAT_RATE = Fraction(7, 100)         # VAT 7% (ขั้นสุดท้าย)


def _check_int(name, value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม ได้ {value!r}")


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่าย (จำนวนเต็มสตางค์)

    unit_price: ราคาต่อถุงเป็นสตางค์ (>= 0)
    qty: จำนวนถุง (1 ถึง 1000)
    coupon: True ถ้ามีคูปอง
    """
    _check_int("unit_price", unit_price)
    _check_int("qty", qty)
    if unit_price < 0:
        raise ValueError(f"unit_price ต้องไม่ติดลบ ได้ {unit_price}")
    if not 1 <= qty <= 1000:
        raise ValueError(f"qty ต้องอยู่ระหว่าง 1 ถึง 1000 ได้ {qty}")

    # 1. ยอดตั้งต้น
    total = Fraction(unit_price * qty)

    # 2. ส่วนลดขายส่ง (อัตราเดียว ไม่สะสม)
    if qty >= 50:
        total *= 1 - BULK_TIER_50
    elif qty >= 10:
        total *= 1 - BULK_TIER_10

    # 3. คูปองลดต่อจากยอดหลังขายส่ง
    if coupon:
        total *= 1 - COUPON_RATE

    # 4. VAT ขั้นสุดท้าย
    total *= 1 + VAT_RATE

    # 5. ปัดครั้งเดียว ครึ่งเข้าเลขคู่
    return round(total)


if __name__ == "__main__":
    print(bulk_price(10000, 1, False))   # 10,000 สตางค์ + VAT 7% = 10,700
    print(bulk_price(10000, 10, True))
    print(bulk_price(10000, 50, True))
