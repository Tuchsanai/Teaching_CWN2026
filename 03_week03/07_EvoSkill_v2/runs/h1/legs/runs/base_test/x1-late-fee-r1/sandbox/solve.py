"""ค่าปรับการชำระเงินล่าช้าของลูกค้าขายส่ง BaanKafe

กติกา:
- amount: ยอดค้างชำระ หน่วยเป็นสตางค์ (จำนวนเต็ม >= 0)
- days_late: จำนวนวันที่ชำระช้า (จำนวนเต็ม 0–365)
- ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน คิดค่าปรับวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุดไม่เกิน 15% ของยอดค้างชำระ
- ผลลัพธ์เป็นจำนวนเต็มสตางค์

การคำนวณใช้จำนวนเต็มล้วนเพื่อหลีกเลี่ยงความคลาดเคลื่อนของ float
- ค่าปรับดิบ = amount * 0.75% * days_late = amount * 75 * days_late / 10000
- ปัดเศษแบบ round half up (ปัดขึ้นเมื่อเศษ >= ครึ่ง)
- เพดาน = floor(amount * 15 / 100); เนื่องจากค่าปรับเป็นจำนวนเต็ม
  การเทียบ fee <= 0.15*amount เท่ากับ fee <= floor(0.15*amount)
"""

GRACE_DAYS = 3
DAILY_RATE_BP = 75        # 0.75% = 75 basis points ต่อวัน (1 bp = 0.01%)
BP_DIVISOR = 10_000
CAP_PERCENT = 15          # เพดาน 15% ของยอดค้างชำระ
MAX_DAYS = 365


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับล่าช้า (สตางค์, จำนวนเต็ม)"""
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

    raw_fee = (amount * DAILY_RATE_BP * days_late + BP_DIVISOR // 2) // BP_DIVISOR
    cap = amount * CAP_PERCENT // 100
    return min(raw_fee, cap)


if __name__ == "__main__":
    # ตัวอย่างการใช้งานและการตรวจสอบเบื้องต้น
    assert late_fee(100_000, 0) == 0
    assert late_fee(100_000, 3) == 0          # ช้า 3 วันยังไม่คิด
    assert late_fee(100_000, 4) == 3_000      # 4 * 0.75% = 3%
    assert late_fee(100_000, 10) == 7_500     # 10 * 0.75% = 7.5%
    assert late_fee(100_000, 20) == 15_000    # ถึงเพดาน 15%
    assert late_fee(100_000, 21) == 15_000    # ไม่เกินเพดาน
    assert late_fee(100_000, 365) == 15_000
    assert late_fee(0, 100) == 0
    assert late_fee(1, 4) == 0                # 0.03 สตางค์ ปัดลงเป็น 0
    assert late_fee(10, 4) == 0               # 0.3 สตางค์ ปัดเป็น 0
    assert late_fee(70, 4) == 2               # 2.1 สตางค์ -> 2
    assert late_fee(67, 4) == 2               # 2.01 สตางค์ -> 2
    assert late_fee(200, 4) == 6              # 6 สตางค์พอดี
    print("ผ่านการทดสอบทั้งหมด")
