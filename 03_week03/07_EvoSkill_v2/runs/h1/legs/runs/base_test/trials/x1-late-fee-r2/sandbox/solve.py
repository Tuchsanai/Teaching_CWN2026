"""ค่าปรับการชำระเงินช้าของลูกค้าขายส่ง BaanKafe

กติกา
- amount     : ยอดค้างชำระ หน่วยเป็นสตางค์ (จำนวนเต็ม >= 0)
- days_late  : จำนวนวันที่ชำระช้า (จำนวนเต็ม 0-365)
- ช้าไม่เกิน 3 วัน -> ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน  -> คิด 0.75% ต่อวันของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุดไม่เกิน 15% ของยอดค้างชำระ
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น)

คำนวณด้วยจำนวนเต็มล้วนเพื่อหลีกเลี่ยงความคลาดเคลื่อนของทศนิยม
หน่วยกลาง 1 หน่วย = 1/10000 สตางค์
  อัตรา 0.75% = 75/10000 ต่อวัน, เพดาน 15% = 1500/10000
"""

GRACE_DAYS = 3
MAX_DAYS = 365
DAILY_RATE_BP = 75      # 0.75% = 75 / 10000
CAP_RATE_BP = 1500      # 15%   = 1500 / 10000
SCALE = 10000


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) ของยอดค้างชำระ `amount` ที่ชำระช้า `days_late` วัน"""
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise TypeError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= MAX_DAYS:
        raise ValueError("days_late ต้องอยู่ระหว่าง 0 ถึง 365")

    if days_late <= GRACE_DAYS:
        return 0

    raw = amount * DAILY_RATE_BP * days_late      # หน่วย 1/10000 สตางค์
    cap = amount * CAP_RATE_BP                    # เพดาน 15% หน่วยเดียวกัน
    fee_scaled = min(raw, cap)

    # ปัดครึ่งขึ้นกลับเป็นสตางค์จำนวนเต็ม
    return (fee_scaled + SCALE // 2) // SCALE


if __name__ == "__main__":
    cases = [
        (100000, 0), (100000, 3),   # ไม่คิดค่าปรับ
        (100000, 4),                # 4 * 0.75% = 3% -> 3000
        (100000, 20),               # 15% เท่าเพดาน -> 15000
        (100000, 21),               # ถูกตัดที่เพดาน 15% -> 15000
        (100000, 365),              # ถูกตัดที่เพดาน -> 15000
        (333, 4),                   # 333 * 0.03 = 9.99 -> 10
    ]
    for amt, d in cases:
        print(f"amount={amt:>8} days_late={d:>3} -> fee={late_fee(amt, d)}")
