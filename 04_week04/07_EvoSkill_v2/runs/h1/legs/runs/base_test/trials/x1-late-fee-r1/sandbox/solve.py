"""ค่าปรับการชำระเงินช้าสำหรับลูกค้าขายส่ง BaanKafe

กติกา
- amount    : ยอดค้างชำระ (สตางค์, จำนวนเต็ม >= 0)
- days_late : จำนวนวันที่ชำระช้า (จำนวนเต็ม 0–365)
- ช้าไม่เกิน 3 วัน -> ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน -> คิดวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุด 15% ของยอดค้างชำระ
- คืนค่าปรับเป็นจำนวนเต็มสตางค์

การคำนวณใช้จำนวนเต็มล้วน (ไม่ใช้ float) เพื่อไม่ให้เกิดความคลาดเคลื่อนของทศนิยม
- อัตรา 0.75% = 75 / 10000
- ปัดเศษ: ปัดขึ้นเมื่อ .5 ขึ้นไป (half-up) ไปเป็นสตางค์เต็ม
- เพดาน 15% ปัดลงเป็นสตางค์เต็ม (ค่าปรับเป็นจำนวนเต็ม จึงไม่เกินเพดานจริง)
"""

GRACE_DAYS = 3
DAILY_RATE_NUM = 75          # 0.75% = 75 / 10000
RATE_DEN = 10_000
CAP_NUM = 15                 # 15% = 15 / 100
CAP_DEN = 100
MAX_DAYS = 365


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) สำหรับยอดค้างชำระ amount และจำนวนวันที่ช้า days_late."""
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise TypeError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= MAX_DAYS:
        raise ValueError(f"days_late ต้องอยู่ระหว่าง 0 ถึง {MAX_DAYS}")

    # ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
    if days_late <= GRACE_DAYS:
        return 0

    # ค่าปรับดิบ = amount * 0.75% * days_late, ปัดครึ่งขึ้นเป็นสตางค์เต็ม
    raw_fee = (amount * DAILY_RATE_NUM * days_late + RATE_DEN // 2) // RATE_DEN

    # เพดาน 15% ของยอดค้างชำระ
    cap = amount * CAP_NUM // CAP_DEN

    return min(raw_fee, cap)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(late_fee(100_000, 3))   # 0      (ช้า 3 วัน ยังไม่คิดค่าปรับ)
    print(late_fee(100_000, 4))   # 3000   (0.75% * 4 วัน = 3%)
    print(late_fee(100_000, 20))  # 15000  (ถึงเพดาน 15%)
    print(late_fee(100_000, 365)) # 15000  (ไม่เกินเพดาน)
