"""ค่าปรับการชำระเงินช้า สำหรับลูกค้าขายส่งของ BaanKafe

กติกา
- amount     : ยอดค้างชำระ หน่วยเป็นสตางค์ (จำนวนเต็ม >= 0)
- days_late  : จำนวนวันที่ชำระช้า (จำนวนเต็ม 0–365)
- ช้าไม่เกิน 3 วัน          -> ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน            -> คิดวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุด            -> 15% ของยอดค้างชำระ
- คืนค่าเป็นจำนวนเต็มสตางค์

การคำนวณใช้จำนวนเต็มล้วน (ไม่ใช้ float) เพื่อไม่ให้เกิดความคลาดเคลื่อนของทศนิยม
การปัดเศษ: ปัดครึ่งขึ้น (half up) ไปเป็นสตางค์ที่ใกล้ที่สุด
"""

GRACE_DAYS = 3
MAX_DAYS = 365

# อัตรารายวัน 0.75% = 75 / 10_000
DAILY_RATE_NUM = 75
DAILY_RATE_DEN = 10_000

# เพดาน 15% = 15 / 100
CAP_RATE_NUM = 15
CAP_RATE_DEN = 100


def _round_half_up(numerator: int, denominator: int) -> int:
    """หาร numerator/denominator (ทั้งคู่ไม่ติดลบ) แล้วปัดครึ่งขึ้นเป็นจำนวนเต็ม"""
    return (numerator * 2 + denominator) // (denominator * 2)


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) สำหรับยอดค้างชำระ `amount` ที่ชำระช้า `days_late` วัน"""
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise TypeError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= MAX_DAYS:
        raise ValueError(f"days_late ต้องอยู่ในช่วง 0–{MAX_DAYS}")

    if days_late <= GRACE_DAYS:
        return 0

    fee = _round_half_up(amount * DAILY_RATE_NUM * days_late, DAILY_RATE_DEN)
    cap = _round_half_up(amount * CAP_RATE_NUM, CAP_RATE_DEN)
    return min(fee, cap)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    examples = [
        (100_000, 0),   # 0
        (100_000, 3),   # 0  (ไม่เกิน 3 วัน)
        (100_000, 4),   # 3,000  (0.75% * 4 วัน = 3%)
        (100_000, 10),  # 7,500
        (100_000, 20),  # 15,000 (ถึงเพดาน 15%)
        (100_000, 365), # 15,000 (ถูกจำกัดที่เพดาน)
        (333, 5),       # 12 (0.75% * 5 * 333 = 12.4875 -> ปัดเป็น 12)
    ]
    for amt, d in examples:
        print(f"amount={amt:>8} days_late={d:>3} -> fee={late_fee(amt, d)}")
