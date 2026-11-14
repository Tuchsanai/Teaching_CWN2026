"""ค่าปรับการชำระเงินช้าของลูกค้าขายส่ง BaanKafe

หน่วยเงินทั้งหมดเป็นสตางค์ (จำนวนเต็ม)
- ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน คิดวันละ 0.75% ของยอดค้างชำระ นับทุกวัน (รวม 3 วันแรก)
- ค่าปรับสูงสุด 15% ของยอดค้างชำระ
- ปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียวตอนท้าย (ลูกค้าจ่ายเข้าร้าน)

ไม่มี side effect ตอน import
"""
import math
from fractions import Fraction

GRACE_DAYS = 3
DAILY_RATE = Fraction(75, 10000)  # 0.75% ต่อวัน
MAX_RATE = Fraction(15, 100)      # เพดาน 15% ของยอดค้างชำระ
MAX_DAYS = 365


def _need_int(value, name, low=None, high=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ)"""
    return math.floor(Fraction(x) + Fraction(1, 2))


def late_fee(amount, days_late):
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม)

    amount    : ยอดค้างชำระ (สตางค์) ตั้งแต่ 0
    days_late : จำนวนวันที่ชำระช้า จำนวนเต็ม 0–365
    """
    amount = _need_int(amount, "amount", low=0)
    days_late = _need_int(days_late, "days_late", low=0, high=MAX_DAYS)

    if days_late <= GRACE_DAYS:
        return 0

    fee = Fraction(amount) * DAILY_RATE * days_late
    cap = Fraction(amount) * MAX_RATE
    return _half_up(min(fee, cap))


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน (ยอด 100 บาท = 10000 สตางค์)
    for amount, days in [(10000, 3), (10000, 4), (10000, 20), (10000, 365)]:
        print(f"amount={amount} days_late={days} -> fee={late_fee(amount, days)}")
