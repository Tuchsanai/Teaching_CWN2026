"""BaanKafe: คำนวณค่าปรับลูกค้าขายส่งที่ชำระเงินช้า

กฎ
- amount     : ยอดค้างชำระ (สตางค์, จำนวนเต็ม >= 0)
- days_late  : จำนวนวันที่ช้า (จำนวนเต็ม 0-365)
- ช้าไม่เกิน 3 วัน            -> ค่าปรับ 0
- ช้าเกิน 3 วัน               -> 0.75% ของยอดค้างชำระ ต่อวันที่ช้า (นับทุกวัน รวม 3 วันแรก)
- ค่าปรับสูงสุด              -> 15% ของยอดค้างชำระ
- ผลลัพธ์เป็นจำนวนเต็มสตางค์

การปัดเศษ: คำนวณด้วยจำนวนเต็มล้วน (ไม่ใช้ float) และปัดครึ่งขึ้นเป็นสตางค์ที่ใกล้ที่สุด
เพดาน 15% ปัดลงเป็นสตางค์ เพื่อไม่ให้ค่าปรับเกินเพดาน
"""

GRACE_DAYS = 3
RATE_BP = 75        # 0.75% = 75 / 10000
RATE_DENOM = 10000
CAP_PCT = 15        # 15% = 15 / 100


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) สำหรับยอดค้างชำระ amount และจำนวนวันที่ช้า days_late"""
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise TypeError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= 365:
        raise ValueError("days_late ต้องอยู่ระหว่าง 0 ถึง 365")

    if days_late <= GRACE_DAYS:
        return 0

    # ค่าปรับดิบ = amount * 0.0075 * days_late  -> ปัดครึ่งขึ้นด้วยจำนวนเต็ม
    raw_fee = (amount * RATE_BP * days_late + RATE_DENOM // 2) // RATE_DENOM

    # เพดาน = floor(amount * 15%)
    cap = (amount * CAP_PCT) // 100

    return min(raw_fee, cap)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    examples = [
        (10000, 0),     # 0
        (10000, 3),     # 0   (ไม่เกิน 3 วัน)
        (10000, 4),     # 300  = 100 บาท * 0.75% * 4 วัน
        (10000, 30),    # 1500 = ถึงเพดาน 15%
        (1234, 7),      # 65   = round(1234 * 0.0075 * 7) = round(64.8) = 65
        (0, 100),       # 0
    ]
    for amt, d in examples:
        print(f"amount={amt:>6}  days_late={d:>3}  fee={late_fee(amt, d)}")
