"""BaanKafe: คำนวณเงินคืนสำหรับคอร์สสอนชงกาแฟ

หน่วยเงินทั้งหมดเป็นสตางค์ (จำนวนเต็ม) ผลลัพธ์เป็นจำนวนเต็มสตางค์
การปัดเศษ: ปัดครึ่งขึ้น (round half up) ด้วยจำนวนเต็มล้วน ไม่ใช้ float
"""


def refund(paid, used_percent, restock):
    """คืนค่าจำนวนเงินที่ต้องคืนให้ลูกค้า (สตางค์)

    paid          -- เงินที่ลูกค้าจ่าย (สตางค์, >= 0)
    used_percent  -- เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock       -- True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    if not isinstance(paid, int) or isinstance(paid, bool) or paid < 0:
        raise ValueError("paid ต้องเป็นจำนวนเต็มที่ไม่ติดลบ (สตางค์)")
    if not isinstance(used_percent, int) or isinstance(used_percent, bool) \
            or not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็ม 0-100")

    # เรียนไปแล้วเกิน 80% ไม่คืนเงิน
    if used_percent > 80:
        return 0

    # ยอดคืนก่อนหักค่าดำเนินการ = paid * (100 - used) / 100
    numerator = paid * (100 - used_percent)
    denominator = 100

    # หักค่าดำเนินการ 12.5% -> เหลือ 87.5% = 875/1000
    if restock:
        numerator *= 875
        denominator *= 1000

    # ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์
    return (2 * numerator + denominator) // (2 * denominator)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(refund(10000, 0, False))   # 10000
    print(refund(10000, 0, True))    # 8750
    print(refund(10000, 50, False))  # 5000
    print(refund(10000, 50, True))   # 4375
    print(refund(10000, 80, False))  # 2000
    print(refund(10000, 81, False))  # 0
