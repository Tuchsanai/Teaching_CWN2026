from fractions import Fraction


def _require_int(value, name, low=None, high=None):
    if type(value) is not int:  # ปฏิเสธ bool, float, str, None
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
    """ปัดครึ่งขึ้นเป็น int, x ไม่ติดลบ (ใช้ Fraction ทั้งหมด ไม่มี float)"""
    return int((Fraction(x) * 2 + 1) // 2)


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นสตางค์ (จำนวนเต็ม)

    unit_price : ราคาต่อถุง (สตางค์, >= 0)
    qty        : จำนวนถุง (1-1000)
    coupon     : True ถ้ามีคูปอง
    """
    unit_price = _require_int(unit_price, "unit_price", low=0)
    qty = _require_int(qty, "qty", low=1, high=1000)
    coupon = _require_bool(coupon, "coupon")

    # 1) ยอดรวมก่อนลด (ยังไม่ปัด)
    total = Fraction(unit_price * qty)

    # 2) ส่วนลดขายส่ง อัตราเดียว (ไม่ทบกัน)
    if qty >= 50:
        total *= Fraction(925, 1000)  # ลด 7.5%
    elif qty >= 10:
        total *= Fraction(965, 1000)  # ลด 3.5%

    # 3) คูปอง ลดอีก 2.5% คิดต่อจากยอดหลังขายส่ง
    if coupon:
        total *= Fraction(975, 1000)

    # 4) VAT 7% เป็นขั้นสุดท้าย
    total *= Fraction(107, 100)

    # 5) ปัดครั้งเดียวตอนท้าย: ยอดที่ลูกค้าจ่ายให้ร้าน -> ปัดครึ่งขึ้น
    return _half_up(total)


if __name__ == "__main__":
    print(bulk_price(10000, 1, False))   # 10,700
    print(bulk_price(10000, 10, False))  # 103,255
    print(bulk_price(10000, 50, True))   # 482,503 (500,000 * 0.925 * 0.975 * 1.07)
