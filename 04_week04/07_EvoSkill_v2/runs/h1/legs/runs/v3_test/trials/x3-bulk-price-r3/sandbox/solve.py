from fractions import Fraction


def _require_int(value, name, low=None, high=None):
    # type(...) is int ปฏิเสธ bool, float, str และ None
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
    """ปัดครึ่งขึ้นเป็น int, x ไม่ติดลบ (ใช้ Fraction เท่านั้น)"""
    return int((Fraction(x) * 2 + 1) // 2)


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    unit_price: ราคาต่อถุง (สตางค์, int, >= 0)
    qty:        จำนวนถุง (int, 1–1000)
    coupon:     True ถ้ามีคูปอง
    """
    # ตรวจ input ก่อนคำนวณทุกอย่าง
    unit_price = _require_int(unit_price, "unit_price", low=0)
    qty = _require_int(qty, "qty", low=1, high=1000)
    coupon = _require_bool(coupon, "coupon")

    # ใช้ Fraction ตลอด ไม่มี float และยังไม่ปัดระหว่างทาง
    total = Fraction(unit_price * qty)

    # ส่วนลดขายส่ง อัตราเดียว (ไม่สะสมกัน)
    if qty >= 50:
        total *= Fraction(925, 1000)   # ลด 7.5%
    elif qty >= 10:
        total *= Fraction(965, 1000)   # ลด 3.5%

    # คูปองลดอีก 2.5% คิดต่อจากยอดที่ลดแล้ว
    if coupon:
        total *= Fraction(975, 1000)

    # VAT 7% เป็นขั้นสุดท้าย
    total *= Fraction(107, 100)

    # ปัดครั้งเดียวตอนท้าย ร้านเป็นฝ่ายรับเงิน จึงปัดครึ่งขึ้น
    return _half_up(total)


if __name__ == "__main__":
    print(bulk_price(10000, 1, False))
    print(bulk_price(10000, 10, False))
    print(bulk_price(10000, 50, True))
