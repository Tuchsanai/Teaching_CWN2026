"""คำนวณเงินคืนของคอร์สสอนชงกาแฟ BaanKafe

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม)
"""

from fractions import Fraction

# เกินกว่านี้ (เรียนไปแล้วมากกว่า 80%) ไม่คืนเงิน
NO_REFUND_THRESHOLD = 80

# ค่าดำเนินการ 12.5% ของยอดที่จะคืน
RESTOCK_FEE_RATE = Fraction(125, 1000)


def refund(paid: int, used_percent: int, restock: bool) -> int:
    """คืนยอดเงินที่ต้องคืนให้ลูกค้า (สตางค์, จำนวนเต็ม)

    paid          เงินที่ลูกค้าจ่ายมา (สตางค์, >= 0)
    used_percent  เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock       True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน

    ปัดเศษลงเป็นจำนวนเต็มสตางค์ (ทศนิยมที่เหลือตัดทิ้ง)
    คำนวณด้วย Fraction เพื่อไม่ให้เกิดความคลาดเคลื่อนของ float
    """
    if paid < 0:
        raise ValueError("paid must be >= 0")
    if not (0 <= used_percent <= 100):
        raise ValueError("used_percent must be between 0 and 100")

    if used_percent > NO_REFUND_THRESHOLD:
        return 0

    # ส่วนที่ยังไม่ได้เรียนตามสัดส่วน
    unused = Fraction(paid) * (100 - used_percent) / 100

    if restock:
        unused -= unused * RESTOCK_FEE_RATE

    return int(unused)  # ปัดลง (floor) เพราะค่าเป็นบวกเสมอ
