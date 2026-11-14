from fractions import Fraction

GRACE_DAYS = 3          # ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
DAILY_RATE = Fraction(75, 10000)  # 0.75% ต่อวัน (เก็บเป็นเศษส่วนเพื่อไม่ให้ float คลาดเคลื่อน)
CAP_RATE = Fraction(15, 100)       # เพดาน 15% ของยอดค้างชำระ


def late_fee(amount, days_late):
    """คืนค่าปรับ (สตางค์, int) ของยอดค้างชำระ amount (สตางค์) ที่ชำระช้า days_late วัน

    - ช้าไม่เกิน 3 วัน: ไม่คิดค่าปรับ
    - ช้าเกิน 3 วัน: คิด 0.75% ต่อวันของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
    - เพดาน: ไม่เกิน 15% ของยอดค้างชำระ
    - ปัดเศษครั้งเดียวที่ขั้นสุดท้าย ด้วยโหมดปัดครึ่งเข้าเลขคู่ (round-half-even)
    """
    if not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if not isinstance(days_late, int) or isinstance(days_late, bool) or not 0 <= days_late <= 365:
        raise ValueError("days_late ต้องเป็นจำนวนเต็มระหว่าง 0 ถึง 365")

    if days_late <= GRACE_DAYS:
        return 0

    fee = min(Fraction(amount) * DAILY_RATE * days_late, Fraction(amount) * CAP_RATE)

    return round(fee)  # ปัดครั้งเดียว: round(Fraction) ใช้ round-half-even


if __name__ == "__main__":
    print(late_fee(100000, 3))   # 0
    print(late_fee(100000, 4))   # 3000  (0.75% × 100,000 × 4 วัน)
    print(late_fee(100000, 20))  # 15000 (ถึงเพดานพอดี)
    print(late_fee(100000, 365)) # 15000 (ชนเพดาน)
