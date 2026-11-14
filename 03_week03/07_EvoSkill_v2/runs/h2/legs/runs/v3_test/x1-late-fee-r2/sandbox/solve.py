"""ค่าปรับการชำระเงินล่าช้าของลูกค้าขายส่ง BaanKafe

กติกา:
- amount: ยอดค้างชำระ หน่วยสตางค์ (จำนวนเต็ม >= 0)
- days_late: จำนวนวันที่ช้า (จำนวนเต็ม 0-365)
- ช้าไม่เกิน 3 วัน: ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน: ค่าปรับ = 0.75% ต่อวัน ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- เพดาน: ไม่เกิน 15% ของยอดค้างชำระ
- ผลลัพธ์เป็นจำนวนเต็มสตางค์

ลำดับการคิด:
1. คำนวณค่าปรับดิบ = amount × 0.75/100 × days_late (ใช้ Fraction ไม่มีการปัดระหว่างทาง)
2. ตัดด้วยเพดาน 15% ของ amount
3. ปัดครั้งเดียวที่ขั้นสุดท้ายแบบปัดครึ่งเข้าเลขคู่ (ค่าเริ่มต้นของ satang-money-math)
   และตัดให้ไม่เกิน floor(เพดาน) เพื่อให้ผลลัพธ์ไม่เกิน 15% แม้ปัดขึ้น
"""

from fractions import Fraction
import math

DAILY_RATE = Fraction(75, 10000)   # 0.75% ต่อวัน
CAP_RATE = Fraction(15, 100)       # เพดาน 15%
GRACE_DAYS = 3                     # ช้าไม่เกิน 3 วันไม่คิดค่าปรับ


def late_fee(amount, days_late):
    """คืนค่าปรับล่าช้า (สตางค์, จำนวนเต็ม)"""
    if not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if not isinstance(days_late, int) or isinstance(days_late, bool) or not (0 <= days_late <= 365):
        raise ValueError("days_late ต้องเป็นจำนวนเต็มระหว่าง 0 ถึง 365")

    if days_late <= GRACE_DAYS:
        return 0

    raw = Fraction(amount) * DAILY_RATE * days_late    # 1. ค่าปรับดิบ
    cap = Fraction(amount) * CAP_RATE                  # 2. เพดาน 15%
    capped = min(raw, cap)

    rounded = round(capped)                            # 3. ปัดครั้งเดียว (ครึ่งเข้าเลขคู่)
    return min(rounded, math.floor(cap))               # ไม่เกินเพดาน 15%


if __name__ == "__main__":
    print(late_fee(100000, 4))    # 3000
    print(late_fee(100000, 3))    # 0
    print(late_fee(100000, 200))  # 15000 (ชนเพดาน)
