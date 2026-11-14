from fractions import Fraction


def _require_int(value, name, low=None, high=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


def _require_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int สำหรับค่าไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นสตางค์ (int)

    - unit_price: ราคาต่อถุง (สตางค์, >= 0)
    - qty: จำนวนถุง (1–1000)
    - coupon: True ถ้ามีคูปอง
    """
    unit_price = _require_int(unit_price, "unit_price", low=0)
    qty = _require_int(qty, "qty", low=1, high=1000)
    coupon = _require_bool(coupon, "coupon")

    # ส่วนลดตามจำนวน (อัตราเดียว ไม่สะสมขั้น)
    if qty >= 50:
        volume_rate = Fraction(75, 1000)   # 7.5%
    elif qty >= 10:
        volume_rate = Fraction(35, 1000)   # 3.5%
    else:
        volume_rate = Fraction(0)

    total = Fraction(unit_price * qty)     # ยังไม่ปัด
    total *= 1 - volume_rate               # ลดตามจำนวน
    if coupon:
        total *= 1 - Fraction(25, 1000)    # ลดอีก 2.5% คิดต่อจากยอดหลังลดข้อแรก
    total *= 1 + Fraction(7, 100)          # VAT 7% เป็นขั้นสุดท้าย

    return _half_up(total)                 # ปัดครั้งเดียว ครึ่งขึ้น (ลูกค้าจ่ายให้ร้าน)
