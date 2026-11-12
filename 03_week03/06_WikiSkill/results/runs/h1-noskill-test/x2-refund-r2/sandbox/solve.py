"""BaanKafe: คำนวณเงินคืนคอร์สสอนชงกาแฟ

กฎ:
- คืนตามสัดส่วนของส่วนที่ยังไม่ได้เรียน (100 - used_percent)%
- เรียนไปแล้วเกิน 80% ไม่คืนเงิน (80% พอดียังคืนได้)
- ถ้า restock=True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดเศษแบบครึ่งขึ้น)

คำนวณด้วยจำนวนเต็มล้วนเพื่อหลีกเลี่ยงความคลาดเคลื่อนของ float
"""


def refund(paid: int, used_percent: int, restock: bool) -> int:
    """คืนยอดเงินที่ต้องคืนลูกค้า (หน่วยเป็นสตางค์)

    paid          เงินที่ลูกค้าจ่ายมา (สตางค์, >= 0)
    used_percent  เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock       True = หักค่าดำเนินการ 12.5%
    """
    if isinstance(paid, bool) or not isinstance(paid, int) or paid < 0:
        raise ValueError("paid ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int) \
            or not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็มระหว่าง 0 ถึง 100")

    if used_percent > 80:
        return 0

    unused = 100 - used_percent  # เปอร์เซ็นต์ที่ยังไม่ได้เรียน

    if restock:
        # ยอดคืน = paid * unused/100 * (1 - 12.5/100) = paid * unused * 7 / 800
        numerator = paid * unused * 7
        denominator = 800
    else:
        numerator = paid * unused
        denominator = 100

    # ปัดเศษแบบครึ่งขึ้นด้วยจำนวนเต็มล้วน
    return (numerator + denominator // 2) // denominator


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(refund(100_000, 0, False))   # 100000
    print(refund(100_000, 50, False))  # 50000
    print(refund(100_000, 50, True))   # 43750
    print(refund(100_000, 80, True))   # 17500
    print(refund(100_000, 81, False))  # 0
