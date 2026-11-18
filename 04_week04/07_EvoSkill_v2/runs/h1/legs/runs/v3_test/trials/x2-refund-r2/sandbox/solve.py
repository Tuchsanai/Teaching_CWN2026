from fractions import Fraction


def _require_int(value, name, low=None, high=None):
    # ปฏิเสธ bool, float, str, None (ตาม strict-input-validation)
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


def refund(paid, used_percent, restock):
    """คำนวณเงินคืนของคอร์สสอนชงกาแฟ (หน่วยเป็นสตางค์, คืนเป็น int)

    paid         : เงินที่ลูกค้าจ่าย (สตางค์, >= 0)
    used_percent : เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock      : True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    paid = _require_int(paid, "paid", low=0)
    used_percent = _require_int(used_percent, "used_percent", low=0, high=100)
    restock = _require_bool(restock, "restock")

    # เรียนไปแล้วเกิน 80% ไม่คืนเงิน
    if used_percent > 80:
        return 0

    # คืนตามสัดส่วนที่ยังไม่ได้เรียน (ยังไม่ปัด)
    amount = Fraction(paid) * Fraction(100 - used_percent, 100)

    # หักค่าดำเนินการ 12.5% = 1/8 ของยอดที่จะคืน
    if restock:
        amount -= amount * Fraction(1, 8)

    # เงินที่ร้านจ่ายออกให้ลูกค้า -> ปัดลง (floor) ครั้งเดียวตอนท้าย
    return int(amount // 1)


if __name__ == "__main__":
    print(refund(10000, 0, False))   # 10000
    print(refund(10000, 0, True))    # 8750
    print(refund(10000, 80, False))  # 2000
    print(refund(10000, 81, False))  # 0
