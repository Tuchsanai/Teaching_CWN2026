from fractions import Fraction

GRACE_DAYS = 3          # ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
DAILY_RATE_BP = 75      # 0.75% ต่อวัน (หน่วย: 1/10000)
CAP_PERCENT = 15        # ค่าปรับสูงสุด 15% ของยอดค้างชำระ


def late_fee(amount, days_late):
    """คืนค่าปรับล่าช้า (จำนวนเต็มสตางค์)

    - amount: ยอดค้างชำระ (สตางค์, >= 0)
    - days_late: จำนวนวันที่ช้า (จำนวนเต็ม 0-365)

    กติกา:
    1. ช้าไม่เกิน 3 วัน -> ค่าปรับ 0
    2. ช้าเกิน 3 วัน -> คิด 0.75% ต่อวันของยอด นับทุกวันที่ช้า (รวม 3 วันแรก)
    3. เพดาน 15% ของยอด (ตัดที่ขั้นสุดท้าย)
    4. ปัดเศษครั้งเดียวที่ขั้นสุดท้าย ด้วยปัดครึ่งเข้าเลขคู่ (round-half-even)
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise ValueError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= 365:
        raise ValueError("days_late ต้องอยู่ระหว่าง 0 ถึง 365")

    if days_late <= GRACE_DAYS:
        return 0

    # ใช้ Fraction ทั้งหมดเพื่อหลีกเลี่ยงความคลาดของ float
    fee = Fraction(amount * DAILY_RATE_BP * days_late, 10000)
    cap = Fraction(amount * CAP_PERCENT, 100)
    fee = min(fee, cap)

    return round(fee)  # round(Fraction) ใช้ round-half-even
