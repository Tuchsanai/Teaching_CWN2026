"""BaanKafe: คำนวณค่าปรับลูกค้าขายส่งที่ชำระเงินช้า

กติกา
- amount     : ยอดค้างชำระ หน่วยเป็นสตางค์ (จำนวนเต็ม >= 0)
- days_late  : จำนวนวันที่ชำระช้า (จำนวนเต็ม 0–365)
- ช้าไม่เกิน 3 วัน          -> ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน              -> ปรับวันละ 0.75% ของยอดค้างชำระ นับทุกวัน (รวม 3 วันแรก)
- ค่าปรับสูงสุด              -> 15% ของยอดค้างชำระ
- ผลลัพธ์                    -> จำนวนเต็มสตางค์ (ปัดเศษแบบ half-up)

การคำนวณใช้จำนวนเต็มล้วน (ไม่ใช้ float) เพื่อไม่ให้ค่าคลาดเคลื่อนจากการปัดเศษของทศนิยม
อัตรา 0.75% = 75/10000 และ 15% = 1500/10000
"""

GRACE_DAYS = 3
MAX_DAYS = 365
DAILY_RATE_BP = 75      # 0.75% ต่อวัน ในหน่วย 1/10000
CAP_RATE_BP = 1500      # 15% ในหน่วย 1/10000
DENOM = 10000


def late_fee(amount, days_late):
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) สำหรับยอดค้าง amount สตางค์ ที่ชำระช้า days_late วัน"""
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise ValueError("days_late ต้องเป็นจำนวนเต็ม")
    if not 0 <= days_late <= MAX_DAYS:
        raise ValueError("days_late ต้องอยู่ระหว่าง 0 ถึง 365")

    if days_late <= GRACE_DAYS:
        return 0

    # ค่าปรับดิบ (ในหน่วย 1/10000 สตางค์) แล้วจำกัดไม่เกินเพดาน 15%
    raw = amount * DAILY_RATE_BP * days_late
    cap = amount * CAP_RATE_BP
    numerator = min(raw, cap)

    # ปัดเศษแบบ half-up เป็นจำนวนเต็มสตางค์
    return (numerator + DENOM // 2) // DENOM


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(late_fee(100_000, 0))   # 0
    print(late_fee(100_000, 3))   # 0
    print(late_fee(100_000, 4))   # 3000  (3%)
    print(late_fee(100_000, 20))  # 15000 (ถึงเพดาน 15%)
    print(late_fee(100_000, 365)) # 15000 (ไม่เกินเพดาน)
