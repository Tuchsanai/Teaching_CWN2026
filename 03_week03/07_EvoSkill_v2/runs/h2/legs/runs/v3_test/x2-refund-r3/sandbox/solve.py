from fractions import Fraction

# คอร์สสอนชงกาแฟ BaanKafe: คิดเงินคืนตามสัดส่วนที่ยังไม่ได้เรียน
#
# กติกา (ทำตามลำดับนี้):
# 1. ตรวจ input: paid >= 0 (หน่วยสตางค์), used_percent เป็นจำนวนเต็ม 0..100
# 2. ถ้าเรียนไปแล้วเกิน 80% (used_percent > 80) ไม่คืนเงิน -> 0
# 3. ยอดตามสัดส่วนที่ยังไม่ได้เรียน = paid * (100 - used_percent) / 100
# 4. ถ้า restock เป็น True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
#    -> ยอดคืน = ยอดข้อ 3 * (1 - 12.5/100) = ยอดข้อ 3 * 7/8
# 5. ปัดเป็นจำนวนเต็มสตางค์ "ครั้งเดียวที่ขั้นสุดท้าย"
#    โหมดปัด: ปัดครึ่งเข้าเลขคู่ (round-half-even) ตามค่าเริ่มต้นของสกิล satang-money-math
#    ใช้ Fraction ตลอด ไม่ใช้ float

FEE_PERCENT = Fraction(25, 2)  # 12.5% ค่าดำเนินการ (ใช้เฉพาะเมื่อ restock=True)
CUTOFF_PERCENT = 80            # เรียนเกินเกณฑ์นี้ไม่คืนเงิน


def refund(paid, used_percent, restock):
    """คืนยอดเงินที่ต้องคืนลูกค้า (จำนวนเต็มสตางค์)

    paid: เงินที่ลูกค้าจ่ายมา (สตางค์, จำนวนเต็ม >= 0)
    used_percent: เรียนไปแล้วกี่เปอร์เซ็นต์ (จำนวนเต็ม 0-100)
    restock: True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    if not isinstance(paid, int) or isinstance(paid, bool) or paid < 0:
        raise ValueError("paid ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if (not isinstance(used_percent, int) or isinstance(used_percent, bool)
            or not 0 <= used_percent <= 100):
        raise ValueError("used_percent ต้องเป็นจำนวนเต็มตั้งแต่ 0 ถึง 100")

    # ข้อ 2: เรียนเกิน 80% ไม่คืนเงิน
    if used_percent > CUTOFF_PERCENT:
        return 0

    # ข้อ 3: ยอดตามสัดส่วนที่ยังไม่ได้เรียน (ยังไม่ปัด)
    amount = Fraction(paid) * Fraction(100 - used_percent, 100)

    # ข้อ 4: หักค่าดำเนินการ 12.5% ถ้า restock
    if restock:
        amount = amount * (1 - FEE_PERCENT / 100)

    # ข้อ 5: ปัดครั้งเดียวที่ขั้นสุดท้าย (round-half-even) ได้จำนวนเต็ม
    return int(round(amount))


if __name__ == "__main__":
    print(refund(10000, 20, True))
    print(refund(10000, 20, False))
