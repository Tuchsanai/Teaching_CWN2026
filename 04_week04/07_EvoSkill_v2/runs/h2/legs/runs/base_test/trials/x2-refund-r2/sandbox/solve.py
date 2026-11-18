from fractions import Fraction


def refund(paid, used_percent, restock):
    """คำนวณเงินที่คืนให้ลูกค้าของคอร์สสอนชงกาแฟ BaanKafe (หน่วย: สตางค์, จำนวนเต็ม)

    paid         เงินที่ลูกค้าจ่ายมา (สตางค์, จำนวนเต็ม >= 0)
    used_percent เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock      True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    if isinstance(paid, bool) or not isinstance(paid, int) or paid < 0:
        raise ValueError("paid ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int) \
            or not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็ม 0-100")

    # เรียนไปแล้วเกิน 80% ไม่คืนเงิน
    if used_percent > 80:
        return 0

    # คืนตามสัดส่วนที่ยังไม่ได้เรียน (ใช้ Fraction เพื่อไม่ให้เกิดความคลาดเคลื่อนของทศนิยม)
    amount = Fraction(paid * (100 - used_percent), 100)

    # หักค่าดำเนินการ 12.5% = 1/8 ของยอดที่จะคืน ⇒ เหลือ 7/8
    if restock:
        amount *= Fraction(7, 8)

    # ปัดลงเป็นจำนวนเต็มสตางค์ (ไม่คืนเกินจริง)
    return int(amount)  # amount >= 0 จึงปัดลงเท่ากับ floor
