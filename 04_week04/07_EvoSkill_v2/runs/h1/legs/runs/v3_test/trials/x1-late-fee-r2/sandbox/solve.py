from fractions import Fraction

GRACE_DAYS = 3                 # ช้าไม่เกินนี้ไม่คิดค่าปรับ
DAILY_RATE = Fraction(75, 10000)  # 0.75% ต่อวัน
MAX_RATE = Fraction(15, 100)      # เพดาน 15% ของยอดค้างชำระ
MAX_DAYS = 365


def _require_int(value, name, low, high=None):
    # ปฏิเสธ bool, float, str และ None ก่อนคำนวณ
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if value < low or (high is not None and value > high):
        raise ValueError(f"{name} ต้องอยู่ระหว่าง {low} ถึง {high}" if high is not None
                         else f"{name} ต้องไม่น้อยกว่า {low}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def late_fee(amount, days_late):
    """คืนค่าปรับ (สตางค์, int) สำหรับยอดค้างชำระ amount ที่ช้า days_late วัน

    - ช้าไม่เกิน 3 วัน: ไม่มีค่าปรับ
    - ช้าเกิน 3 วัน: 0.75% ต่อวันของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
    - เพดาน: 15% ของยอดค้างชำระ
    - ปัดครึ่งขึ้นครั้งเดียวตอนท้าย (ค่าปรับเป็นเงินที่ลูกค้าจ่ายให้ร้าน)
    """
    amount = _require_int(amount, "amount", 0)
    days_late = _require_int(days_late, "days_late", 0, MAX_DAYS)

    if days_late <= GRACE_DAYS:
        return 0

    fee = Fraction(amount) * DAILY_RATE * days_late
    cap = Fraction(amount) * MAX_RATE
    return _half_up(min(fee, cap))


if __name__ == "__main__":
    print(late_fee(10000, 4))   # 300
    print(late_fee(10000, 20))  # 1500 (ถึงเพดาน)
