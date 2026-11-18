from fractions import Fraction

FEE_RATE = Fraction(125, 1000)  # ค่าดำเนินการ 12.5%
NO_REFUND_ABOVE = 80            # เรียนเกิน 80% ไม่คืนเงิน


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


def refund(paid, used_percent, restock):
    """คืนเงินค่าคอร์สสอนชงกาแฟ คืนเป็นจำนวนเต็มสตางค์

    paid         เงินที่ลูกค้าจ่าย (สตางค์, จำนวนเต็ม >= 0)
    used_percent เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock      True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    paid = _require_int(paid, "paid", low=0)
    used_percent = _require_int(used_percent, "used_percent", low=0, high=100)
    restock = _require_bool(restock, "restock")

    if used_percent > NO_REFUND_ABOVE:
        return 0

    # คืนตามสัดส่วนที่ยังไม่ได้เรียน (ยังไม่ปัด)
    amount = Fraction(paid) * Fraction(100 - used_percent, 100)

    # หักค่าดำเนินการ 12.5% ของยอดที่จะคืน (ยังไม่ปัด)
    if restock:
        amount -= amount * FEE_RATE

    # เงินไหลจากร้านไปหาลูกค้า จึงปัดลงครั้งเดียวตอนท้าย
    return int(amount // 1)


if __name__ == "__main__":
    print(refund(10000, 20, False))  # 8000
    print(refund(10000, 20, True))   # 7000
    print(refund(1001, 10, True))    # 788
