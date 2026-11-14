"""คำนวณเงินคืนคอร์สสอนชงกาแฟของ BaanKafe

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม)
"""

from fractions import Fraction
import math

NO_REFUND_THRESHOLD = 80  # เรียนไปแล้วเกินค่านี้ (%) ไม่คืนเงิน
RESTOCK_FEE_NUM = 1       # ค่าดำเนินการ 12.5% = 1/8 ของยอดที่จะคืน
RESTOCK_FEE_DEN = 8


def refund(paid: int, used_percent: int, restock: bool) -> int:
    """คืนจำนวนเงินที่ต้องคืนลูกค้า (สตางค์, จำนวนเต็ม)

    paid          เงินที่ลูกค้าจ่ายมา (สตางค์, >= 0)
    used_percent  เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock       True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน

    การปัดเศษ: คำนวณด้วยเศษส่วนที่แม่นยำ แล้วปัดลง (floor) เป็นสตางค์
    เพื่อไม่ให้คืนเกินสิทธิ์ของลูกค้า
    """
    if isinstance(paid, bool) or not isinstance(paid, int) or paid < 0:
        raise ValueError("paid ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int) \
            or not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็มตั้งแต่ 0 ถึง 100")

    if used_percent > NO_REFUND_THRESHOLD:
        return 0

    # ยอดตามสัดส่วนที่ยังไม่ได้เรียน
    amount = Fraction(paid * (100 - used_percent), 100)

    if restock:
        # หักค่าดำเนินการ 12.5% -> เหลือ 7/8 ของยอด
        amount -= amount * Fraction(RESTOCK_FEE_NUM, RESTOCK_FEE_DEN)

    return math.floor(amount)


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 4:
        paid_arg, used_arg, restock_arg = sys.argv[1:]
        restock_val = restock_arg.lower() in ("1", "true", "yes", "y")
        print(refund(int(paid_arg), int(used_arg), restock_val))
    else:
        # ตัวอย่างการทำงาน
        print(refund(100000, 0, False))   # 1000.00 บาท ยังไม่เรียน -> 100000
        print(refund(100000, 50, False))  # เรียนไป 50% -> 50000
        print(refund(100000, 50, True))   # เรียนไป 50% หักค่าดำเนินการ -> 43750
        print(refund(100000, 81, True))   # เกิน 80% -> 0
