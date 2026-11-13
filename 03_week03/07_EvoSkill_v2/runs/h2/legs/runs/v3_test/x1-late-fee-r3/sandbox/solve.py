"""ค่าปรับลูกค้าขายส่งที่ชำระเงินช้าของร้าน BaanKafe

กติกา (ตามลำดับ):
1. ช้าไม่เกิน 3 วัน (days_late <= 3) ไม่คิดค่าปรับ
2. ช้าเกิน 3 วัน คิดค่าปรับวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
3. ค่าปรับสูงสุด 15% ของยอดค้างชำระ
4. คืนค่าปรับเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น ปัดครั้งเดียวที่ผลลัพธ์)

หน่วย: amount เป็นสตางค์ (int >= 0), days_late เป็นจำนวนเต็ม 0-365
"""

import math
from fractions import Fraction

DAILY_RATE = Fraction(75, 10000)   # 0.75% ต่อวัน
MAX_RATE = Fraction(15, 100)       # เพดาน 15%
GRACE_DAYS = 3
MAX_DAYS = 365


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ใช้กับค่าที่ไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def late_fee(amount, days_late):
    """คืนค่าปรับ (สตางค์, int) ของยอดค้างชำระ amount ที่ช้า days_late วัน"""
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise ValueError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= MAX_DAYS:
        raise ValueError("days_late ต้องอยู่ระหว่าง 0-365")

    # ขั้นที่ 1: ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
    if days_late <= GRACE_DAYS:
        return 0

    # ขั้นที่ 2: อัตราต่อวัน x จำนวนวันที่ช้าทั้งหมด (ยังไม่ปัด)
    fee = amount * DAILY_RATE * days_late

    # ขั้นที่ 3: เพดาน 15% ของยอดค้างชำระ ใช้ค่าจำนวนเต็มสตางค์ที่ไม่เกินเพดาน
    cap = math.floor(amount * MAX_RATE)

    # ขั้นที่ 4: ปัดครึ่งขึ้นครั้งเดียว แล้วจึงใช้เพดาน
    return min(_round_half_up(fee), cap)


if __name__ == "__main__":
    print(late_fee(100000, 3))   # 0
    print(late_fee(100000, 4))   # 3000
    print(late_fee(100000, 10))  # 7500
    print(late_fee(100000, 30))  # 15000 (ชนเพดาน)
