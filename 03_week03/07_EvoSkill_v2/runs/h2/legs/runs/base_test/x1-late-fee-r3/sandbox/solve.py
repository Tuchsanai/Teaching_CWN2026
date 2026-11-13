"""ค่าปรับการชำระเงินล่าช้าของลูกค้าขายส่ง BaanKafe."""

from fractions import Fraction

GRACE_DAYS = 3                     # ช้าไม่เกินนี้ไม่คิดค่าปรับ
DAILY_RATE = Fraction(75, 10000)   # 0.75% ต่อวัน
MAX_RATE = Fraction(15, 100)       # เพดาน 15% ของยอดค้างชำระ
MAX_DAYS = 365


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับเป็นจำนวนเต็มสตางค์

    amount    -- ยอดค้างชำระ (สตางค์, >= 0)
    days_late -- จำนวนวันที่ชำระช้า (0-365)

    - ช้าไม่เกิน 3 วัน: ค่าปรับ 0
    - ช้าเกิน 3 วัน: 0.75% ของยอดค้างชำระ คูณจำนวนวันที่ช้าทั้งหมด (รวม 3 วันแรก)
    - ค่าปรับสูงสุด 15% ของยอดค้างชำระ
    - ปัดเศษแบบครึ่งขึ้น (half-up) ให้เป็นสตางค์เต็ม
    """
    if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์ที่ >= 0")
    if isinstance(days_late, bool) or not isinstance(days_late, int) \
            or not 0 <= days_late <= MAX_DAYS:
        raise ValueError(f"days_late ต้องเป็นจำนวนเต็ม 0-{MAX_DAYS}")

    if days_late <= GRACE_DAYS:
        return 0

    # ใช้ Fraction เพื่อให้คำนวณแม่นยำ ไม่มีค่าคลาดเคลื่อนจาก float
    fee = min(amount * DAILY_RATE * days_late, amount * MAX_RATE)

    # ปัดเศษครึ่งขึ้น: floor(fee + 1/2)
    return int(fee + Fraction(1, 2))


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    assert late_fee(100_000, 3) == 0          # ช้า 3 วัน ไม่คิดค่าปรับ
    assert late_fee(100_000, 4) == 3_000      # 4 * 0.75% = 3%
    assert late_fee(100_000, 20) == 15_000    # 20 * 0.75% = 15% (ถึงเพดาน)
    assert late_fee(100_000, 365) == 15_000   # ถูกจำกัดที่ 15%
    assert late_fee(0, 100) == 0              # ยอด 0 ไม่มีค่าปรับ
    assert late_fee(333, 4) == 10             # 333*0.03 = 9.99 -> 10 (ปัดครึ่งขึ้น)
    assert late_fee(1, 4) == 0                # 0.03 -> 0
    print("ผ่านทุกกรณีทดสอบ")
