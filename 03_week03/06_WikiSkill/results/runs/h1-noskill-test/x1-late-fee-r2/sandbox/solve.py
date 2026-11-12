"""ค่าปรับการชำระเงินช้าสำหรับลูกค้าขายส่ง BaanKafe.

กฎ:
- ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน คิดวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุดไม่เกิน 15% ของยอดค้างชำระ
- คืนค่าเป็นจำนวนเต็มสตางค์ (ปัดเศษแบบครึ่งขึ้น)

การคำนวณทั้งหมดใช้จำนวนเต็มล้วน เพื่อหลีกเลี่ยงความคลาดเคลื่อนของ float.
"""

GRACE_DAYS = 3
DAILY_RATE_BP = 75          # 0.75% = 75 / 10000
MAX_RATE_BP = 1500          # 15%   = 1500 / 10000
BASIS = 10000               # ตัวหารของ basis points


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) สำหรับยอดค้างชำระ `amount` ที่ช้า `days_late` วัน."""
    if not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if not isinstance(days_late, int) or isinstance(days_late, bool) or not 0 <= days_late <= 365:
        raise ValueError("days_late ต้องเป็นจำนวนเต็มระหว่าง 0 ถึง 365")

    if days_late <= GRACE_DAYS:
        return 0

    # ค่าปรับดิบ และเพดาน เก็บในหน่วย "amount * BASIS" เพื่อให้เป็นจำนวนเต็มทั้งหมด
    raw = amount * DAILY_RATE_BP * days_late
    cap = amount * MAX_RATE_BP
    scaled = min(raw, cap)

    # ปัดเศษครึ่งขึ้นไปเป็นสตางค์ที่ใกล้ที่สุด
    return (scaled + BASIS // 2) // BASIS


if __name__ == "__main__":
    # ตัวอย่างการทดสอบอย่างง่าย
    assert late_fee(100_000, 0) == 0
    assert late_fee(100_000, 3) == 0          # ยังไม่เกิน 3 วัน
    assert late_fee(100_000, 4) == 3_000      # 4 * 0.75% = 3%
    assert late_fee(100_000, 20) == 15_000    # 20 * 0.75% = 15% (ถึงเพดานพอดี)
    assert late_fee(100_000, 30) == 15_000    # เกินเพดาน ถูกจำกัดที่ 15%
    assert late_fee(0, 365) == 0
    assert late_fee(1, 10) == 0               # 0.075 สตางค์ ปัดเป็น 0
    assert late_fee(1, 100) == 0              # เพดาน 15% ของ 1 สตางค์ = 0.15 -> 0
    assert late_fee(333, 5) == 12             # 333 * 0.0375 = 12.4875 -> 12
    assert late_fee(1000, 5) == 38            # 1000 * 0.0375 = 37.5 -> 38 (ปัดครึ่งขึ้น)
    print("ผ่านการทดสอบทั้งหมด")
