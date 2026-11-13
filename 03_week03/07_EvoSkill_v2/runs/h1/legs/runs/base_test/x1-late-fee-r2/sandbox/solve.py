"""ค่าปรับการชำระเงินล่าช้าสำหรับลูกค้าขายส่ง BaanKafe

กติกา:
- amount: ยอดค้างชำระ (สตางค์, จำนวนเต็ม >= 0)
- days_late: จำนวนวันที่ช้า (จำนวนเต็ม 0-365)
- ช้าไม่เกิน 3 วัน: ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน: คิด 0.75% ต่อวันของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุด 15% ของยอดค้างชำระ
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดเศษแบบ round half up)

ใช้จำนวนเต็มล้วน: 0.75% = 75/10000, 15% = 1500/10000
"""

GRACE_DAYS = 3
DAILY_RATE_BP = 75     # 0.75% ต่อวัน หน่วยเป็น 1/10000
CAP_RATE_BP = 1500     # 15% หน่วยเป็น 1/10000
SCALE = 10000


def late_fee(amount: int, days_late: int) -> int:
    if not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if not isinstance(days_late, int) or isinstance(days_late, bool) or not 0 <= days_late <= 365:
        raise ValueError("days_late ต้องเป็นจำนวนเต็มระหว่าง 0 ถึง 365")

    if days_late <= GRACE_DAYS:
        return 0

    # หน่วยเป็น "สตางค์ x 1/10000" เพื่อให้คำนวณเป็นจำนวนเต็มทั้งหมด
    raw = amount * DAILY_RATE_BP * days_late
    cap = amount * CAP_RATE_BP
    capped = min(raw, cap)

    # ปัดเศษครึ่งขึ้นกลับเป็นสตางค์
    return (capped + SCALE // 2) // SCALE


if __name__ == "__main__":
    # ตัวอย่างการทดสอบ
    assert late_fee(100_000, 0) == 0
    assert late_fee(100_000, 3) == 0          # ช้า 3 วัน ยังไม่คิด
    assert late_fee(100_000, 4) == 3_000      # 0.75% x 4 = 3% -> 3,000 สตางค์
    assert late_fee(100_000, 10) == 7_500     # 7.5%
    assert late_fee(100_000, 20) == 15_000    # ถึงเพดาน 15% พอดี
    assert late_fee(100_000, 21) == 15_000    # ไม่เกินเพดาน
    assert late_fee(100_000, 365) == 15_000
    assert late_fee(0, 30) == 0
    assert late_fee(333, 4) == 10             # 333 * 0.03 = 9.99 -> 10
    print("ผ่านทุกตัวอย่าง")
