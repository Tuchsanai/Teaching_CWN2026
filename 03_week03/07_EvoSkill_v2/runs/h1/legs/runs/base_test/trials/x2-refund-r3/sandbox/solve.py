"""คำนวณเงินคืนคอร์สสอนชงกาแฟของ BaanKafe

หน่วยเป็นสตางค์ทั้งหมด ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดเศษลง เพื่อไม่จ่ายเกินสิทธิ์)
"""


def refund(paid: int, used_percent: int, restock: bool) -> int:
    """คืนยอดเงินที่ต้องคืนลูกค้า (สตางค์, จำนวนเต็ม)

    paid          เงินที่ลูกค้าจ่ายมา (สตางค์, >= 0)
    used_percent  เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock       True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    if isinstance(paid, bool) or not isinstance(paid, int) or paid < 0:
        raise ValueError("paid ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int) \
            or not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็มระหว่าง 0 ถึง 100")

    # เรียนไปแล้วเกิน 80% ไม่คืนเงิน
    if used_percent > 80:
        return 0

    unused = 100 - used_percent  # สัดส่วนที่ยังไม่ได้เรียน (หน่วย: ร้อยละ)

    if restock:
        # ยอดคืน = paid * unused/100 * (1 - 12.5%) = paid * unused * 7 / 800
        return (paid * unused * 7) // 800

    # ยอดคืน = paid * unused / 100
    return (paid * unused) // 100


if __name__ == "__main__":
    print(refund(100_000, 0, False))   # 100000
    print(refund(100_000, 50, False))  # 50000
    print(refund(100_000, 50, True))   # 43750
    print(refund(100_000, 80, False))  # 20000
    print(refund(100_000, 81, False))  # 0
