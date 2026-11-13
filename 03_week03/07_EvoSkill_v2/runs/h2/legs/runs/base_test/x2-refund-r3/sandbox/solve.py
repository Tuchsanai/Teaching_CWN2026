"""คำนวณเงินคืนคอร์สสอนชงกาแฟของ BaanKafe.

หน่วยทั้งหมดเป็นสตางค์ และผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดเศษลง)
"""


def refund(paid: int, used_percent: int, restock: bool) -> int:
    """คืนยอดเงินที่ต้องคืนให้ลูกค้า.

    paid         เงินที่ลูกค้าจ่าย (สตางค์, จำนวนเต็ม >= 0)
    used_percent เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock      True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    if not isinstance(paid, int) or isinstance(paid, bool) or paid < 0:
        raise ValueError("paid ต้องเป็นจำนวนเต็มสตางค์ที่ >= 0")
    if not isinstance(used_percent, int) or isinstance(used_percent, bool) \
            or not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็ม 0-100")

    # เรียนไปแล้วเกิน 80% ไม่คืนเงิน
    if used_percent > 80:
        return 0

    remaining = 100 - used_percent  # เปอร์เซ็นต์ที่ยังไม่ได้เรียน

    if restock:
        # ยอดคืน = paid * remaining/100 * (1 - 12.5%) = paid * remaining * 7 / 800
        return paid * remaining * 7 // 800

    # ยอดคืน = paid * remaining / 100
    return paid * remaining // 100


if __name__ == "__main__":
    print(refund(100000, 0, False))   # 100000
    print(refund(100000, 50, False))  # 50000
    print(refund(100000, 50, True))   # 43750
    print(refund(100000, 80, True))   # 17500
    print(refund(100000, 81, False))  # 0
