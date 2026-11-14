"""ค่าปรับค้างชำระลูกค้าขายส่ง ร้าน BaanKafe

กติกา
- amount     : ยอดค้างชำระ หน่วยเป็นสตางค์ (จำนวนเต็ม >= 0)
- days_late  : จำนวนวันที่ชำระช้า (จำนวนเต็ม 0–365)
- ช้าไม่เกิน 3 วัน            -> ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน               -> คิดวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุด              -> 15% ของยอดค้างชำระ
- ผลลัพธ์                    -> จำนวนเต็มสตางค์ (ปัดทศนิยมแบบ ROUND_HALF_UP)
"""

from decimal import Decimal, ROUND_HALF_UP

GRACE_DAYS = 3
DAILY_RATE = Decimal("0.0075")   # 0.75% ต่อวัน
MAX_RATE = Decimal("0.15")       # เพดาน 15%
MAX_DAYS = 365


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) ของยอดค้างชำระ `amount` ที่ชำระช้า `days_late` วัน"""
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= MAX_DAYS:
        raise ValueError(f"days_late ต้องอยู่ในช่วง 0–{MAX_DAYS}")

    if days_late <= GRACE_DAYS:
        return 0

    principal = Decimal(amount)
    fee = principal * DAILY_RATE * days_late
    cap = principal * MAX_RATE
    fee = min(fee, cap)

    return int(fee.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


if __name__ == "__main__":
    # ตัวอย่างการทดสอบอย่างง่าย
    cases = [
        (100_000, 0, 0),
        (100_000, 3, 0),        # ไม่เกิน 3 วัน
        (100_000, 4, 3_000),    # 4 วัน: 0.75% * 4 = 3% -> 3,000 สตางค์
        (100_000, 10, 7_500),   # 10 วัน: 7.5%
        (100_000, 20, 15_000),  # 20 วัน: 15% (ถึงเพดานพอดี)
        (100_000, 365, 15_000), # เกินเพดาน -> ตัดที่ 15%
        (0, 30, 0),
        (333, 5, 12),           # 333 * 0.0375 = 12.4875 -> 12
    ]
    for amount, days, expected in cases:
        got = late_fee(amount, days)
        status = "OK " if got == expected else "FAIL"
        print(f"{status} late_fee({amount}, {days}) = {got} (expected {expected})")
