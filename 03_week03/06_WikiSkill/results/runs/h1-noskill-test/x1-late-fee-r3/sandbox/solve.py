"""ค่าปรับการชำระเงินล่าช้าของลูกค้าขายส่ง BaanKafe

กติกา
- amount    : ยอดค้างชำระ หน่วยเป็นสตางค์ (จำนวนเต็ม >= 0)
- days_late : จำนวนวันที่ชำระช้า (จำนวนเต็ม 0–365)
- ช้าไม่เกิน 3 วัน            -> ไม่มีค่าปรับ
- ช้าเกิน 3 วัน               -> คิดวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุด               -> 15% ของยอดค้างชำระ
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ ปัดครึ่งขึ้น

การคำนวณใช้จำนวนเต็มล้วน (หน่วยย่อย 1/10000 ของสตางค์) เพื่อหลีกเลี่ยงข้อผิดพลาดจากทศนิยม
  0.75%  = 75/10000
  15%    = 1500/10000
"""

GRACE_DAYS = 3
MAX_DAYS = 365
DAILY_RATE_BP = 75      # 0.75% ในหน่วย 1/10000
CAP_RATE_BP = 1500      # 15% ในหน่วย 1/10000
SCALE = 10000


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) สำหรับยอดค้างชำระ amount และจำนวนวันที่ช้า days_late"""
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise TypeError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= MAX_DAYS:
        raise ValueError(f"days_late ต้องอยู่ระหว่าง 0 ถึง {MAX_DAYS}")

    if days_late <= GRACE_DAYS:
        return 0

    raw = amount * DAILY_RATE_BP * days_late      # ค่าปรับก่อนเพดาน (หน่วย 1/10000)
    cap = amount * CAP_RATE_BP                    # เพดาน 15% (หน่วย 1/10000)
    fee_scaled = min(raw, cap)
    return (fee_scaled + SCALE // 2) // SCALE     # ปัดครึ่งขึ้น


if __name__ == "__main__":
    # ตัวอย่างการใช้งานและการตรวจสอบเบื้องต้น
    assert late_fee(100_000, 0) == 0
    assert late_fee(100_000, 3) == 0            # ไม่เกิน 3 วัน ไม่คิดค่าปรับ
    assert late_fee(100_000, 4) == 3_000        # 4 วัน * 0.75% = 3%
    assert late_fee(100_000, 10) == 7_500       # 10 วัน * 0.75% = 7.5%
    assert late_fee(100_000, 20) == 15_000      # 20 วัน = 15% (ถึงเพดานพอดี)
    assert late_fee(100_000, 365) == 15_000     # เกินเพดานแล้วต้องถูกตัดที่ 15%
    assert late_fee(0, 100) == 0
    assert late_fee(1, 4) == 0                  # 0.03 สตางค์ ปัดลงเป็น 0
    assert late_fee(1, 200) == 0                # 15% ของ 1 สตางค์ ปัดเป็น 0
    assert late_fee(10, 200) == 2               # 15% ของ 10 สตางค์ = 1.5 ปัดขึ้นเป็น 2
    assert late_fee(3, 4) == 0                  # 0.09 ปัดเป็น 0
    assert late_fee(200, 4) == 6                # 6 สตางค์ พอดี
    print("ทดสอบผ่านทั้งหมด")
