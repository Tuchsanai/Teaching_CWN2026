"""BaanKafe: คำนวณค่าปรับลูกค้าขายส่งที่ชำระเงินช้า

กติกา
- amount    : ยอดค้างชำระ หน่วยเป็นสตางค์ (จำนวนเต็ม >= 0)
- days_late : จำนวนวันที่ชำระช้า (จำนวนเต็ม 0–365)
- ช้าไม่เกิน 3 วัน            -> ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน               -> ค่าปรับ = 0.75% ของยอดค้างชำระ ต่อวัน
                                 นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุด               -> 15% ของยอดค้างชำระ
- ผลลัพธ์                    -> จำนวนเต็มสตางค์ (ปัดเศษแบบครึ่งขึ้น)

การคำนวณใช้จำนวนเต็มล้วน (ไม่ใช้ float) เพื่อหลีกเลี่ยงความคลาดเคลื่อนของทศนิยม
"""

GRACE_DAYS = 3
DAILY_RATE_BP = 75      # 0.75% = 75 / 10_000
CAP_RATE_BP = 1500      # 15%   = 1500 / 10_000
RATE_DENOM = 10_000
MAX_DAYS = 365


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) ของยอดค้างชำระ `amount` ที่ชำระช้า `days_late` วัน"""
    if not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if not isinstance(days_late, int) or isinstance(days_late, bool) \
            or not 0 <= days_late <= MAX_DAYS:
        raise ValueError(f"days_late ต้องเป็นจำนวนเต็มระหว่าง 0 ถึง {MAX_DAYS}")

    if days_late <= GRACE_DAYS:
        return 0

    # หน่วยของตัวเศษคือ 1/10_000 สตางค์ เพื่อให้คงความแม่นยำก่อนการปัดเศษ
    raw_fee_num = amount * DAILY_RATE_BP * days_late
    cap_fee_num = amount * CAP_RATE_BP
    fee_num = min(raw_fee_num, cap_fee_num)

    # ปัดเศษครึ่งขึ้นเป็นจำนวนเต็มสตางค์
    return (fee_num + RATE_DENOM // 2) // RATE_DENOM


if __name__ == "__main__":
    # ตัวอย่างการทดสอบอย่างรวดเร็ว
    cases = [
        (100_000, 0, 0),
        (100_000, 3, 0),       # ไม่เกิน 3 วัน
        (100_000, 4, 3_000),   # 4 วัน * 0.75% = 3%
        (100_000, 20, 15_000), # 20 วัน = 15% พอดีเพดาน
        (100_000, 30, 15_000), # เกินเพดาน ถูกจำกัดที่ 15%
        (100_000, 365, 15_000),
        (1, 4, 0),             # 0.0300 สตางค์ -> ปัดเป็น 0
        (50, 4, 2),            # 1.5 สตางค์ -> ปัดครึ่งขึ้นเป็น 2
    ]
    for amount, days, expected in cases:
        got = late_fee(amount, days)
        status = "OK " if got == expected else "FAIL"
        print(f"{status} late_fee({amount}, {days}) = {got} (expected {expected})")
