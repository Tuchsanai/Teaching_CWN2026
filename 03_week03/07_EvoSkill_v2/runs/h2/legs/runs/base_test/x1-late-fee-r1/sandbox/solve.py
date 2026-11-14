"""ค่าปรับลูกค้าขายส่งของ BaanKafe ที่ชำระเงินช้า

กติกา
- amount     : ยอดค้างชำระ หน่วยเป็นสตางค์ (จำนวนเต็ม >= 0)
- days_late  : จำนวนวันที่ชำระช้า (จำนวนเต็ม 0–365)
- ช้าไม่เกิน 3 วัน            -> ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน              -> ค่าปรับ 0.75% ต่อวันของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุด              -> 15% ของยอดค้างชำระ
- ผลลัพธ์                    -> จำนวนเต็มสตางค์

การคำนวณใช้จำนวนตรรกยะ (Fraction) เพื่อไม่ให้เกิดความคลาดเคลื่อนจากทศนิยมของ float
การปัดเศษ: ปัดครึ่งขึ้น (round half up) เป็นสตางค์
เพดาน 15% ปัดลงเป็นสตางค์ เพื่อไม่ให้ผลลัพธ์เกินเพดานแม้เพียง 1 สตางค์
"""

from fractions import Fraction
import math

GRACE_DAYS = 3
DAILY_RATE = Fraction(75, 10000)   # 0.75%
MAX_RATE = Fraction(15, 100)       # 15%
MAX_DAYS = 365


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) สำหรับยอดค้างชำระ amount และจำนวนวันที่ช้า days_late"""
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise TypeError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= MAX_DAYS:
        raise ValueError(f"days_late ต้องอยู่ระหว่าง 0–{MAX_DAYS}")

    if days_late <= GRACE_DAYS:
        return 0

    fee = amount * DAILY_RATE * days_late          # ค่าปรับดิบ (Fraction)
    cap = amount * MAX_RATE                        # เพดาน 15% (Fraction)

    fee_rounded = math.floor(min(fee, cap) + Fraction(1, 2))  # ปัดครึ่งขึ้น
    cap_floor = math.floor(cap)                               # เพดานปัดลง ไม่ให้เกิน 15%
    return min(fee_rounded, cap_floor)


if __name__ == "__main__":
    # ตัวอย่างการทดสอบอย่างรวดเร็ว
    assert late_fee(100_000, 0) == 0
    assert late_fee(100_000, 3) == 0          # ช้า 3 วันยังไม่คิด
    assert late_fee(100_000, 4) == 3_000      # 4 * 0.75% = 3%
    assert late_fee(100_000, 20) == 15_000    # 20 * 0.75% = 15% (ถึงเพดานพอดี)
    assert late_fee(100_000, 365) == 15_000   # ไม่เกินเพดาน 15%
    assert late_fee(0, 100) == 0
    assert late_fee(1, 4) == 0                # 0.03 สตางค์ ปัดเป็น 0
    assert late_fee(1, 200) == 0              # เพดาน 0.15 สตางค์ ปัดลงเป็น 0
    assert late_fee(333, 10) == 25            # 333*0.075 = 24.975 -> 25
    print("ทดสอบผ่านทั้งหมด")
