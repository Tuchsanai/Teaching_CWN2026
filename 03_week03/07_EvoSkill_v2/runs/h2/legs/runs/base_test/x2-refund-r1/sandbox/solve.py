"""คำนวณเงินคืนคอร์สสอนชงกาแฟ ของร้าน BaanKafe

กติกา
- paid         : เงินที่ลูกค้าจ่าย (สตางค์, จำนวนเต็ม >= 0)
- used_percent : เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
- restock      : True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
- คืนตามสัดส่วนที่ยังไม่ได้เรียน
- เรียนไปแล้วเกิน 80% ไม่คืนเงิน (80 พอดียังคืน)
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ ปัดลง (floor) เพื่อไม่ให้จ่ายเกินสิทธิ์

คำนวณด้วยจำนวนเต็มล้วน เพื่อหลีกเลี่ยงความคลาดเคลื่อนของ float
"""


def refund(paid: int, used_percent: int, restock: bool) -> int:
    if isinstance(paid, bool) or not isinstance(paid, int) or paid < 0:
        raise ValueError("paid ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int) \
            or not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็มระหว่าง 0 ถึง 100")

    # เรียนไปเกิน 80% ไม่คืนเงิน
    if used_percent > 80:
        return 0

    unused = 100 - used_percent
    # ยอดคืนก่อนหักค่าดำเนินการ = paid * unused / 100
    gross_numerator = paid * unused

    if restock:
        # หัก 12.5% (= 1/8) ของยอดคืน: net = gross * 7/8 = paid * unused * 7 / 800
        return gross_numerator * 7 // 800
    return gross_numerator // 100


if __name__ == "__main__":
    print(refund(100_000, 0, False))   # 100000
    print(refund(100_000, 0, True))    # 87500
    print(refund(100_000, 50, False))  # 50000
    print(refund(100_000, 50, True))   # 43750
    print(refund(100_000, 80, True))   # 17500
    print(refund(100_000, 81, False))  # 0
