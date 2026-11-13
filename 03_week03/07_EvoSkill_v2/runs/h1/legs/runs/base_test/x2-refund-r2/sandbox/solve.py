"""คิดเงินคืนของคอร์สสอนชงกาแฟ BaanKafe

หน่วยเป็นสตางค์ทั้งหมด (จำนวนเต็ม) ผลลัพธ์เป็นจำนวนเต็มสตางค์
การปัดเศษ: ปัดลง (floor) เพื่อไม่ให้คืนเกินยอดที่ควรคืน
"""


def refund(paid: int, used_percent: int, restock: bool) -> int:
    """คืนยอดเงินที่ต้องคืนลูกค้า (สตางค์)

    paid          เงินที่ลูกค้าจ่าย (สตางค์, >= 0)
    used_percent  เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock       True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    if isinstance(paid, bool) or not isinstance(paid, int) or paid < 0:
        raise ValueError("paid ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int) \
            or not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็ม 0-100")

    # เรียนเกิน 80% ไม่คืนเงิน
    if used_percent > 80:
        return 0

    # ยอดคืนตามสัดส่วนที่ยังไม่ได้เรียน = paid * (100 - used) / 100
    # หักค่าดำเนินการ 12.5% (= 1/8) -> ยอดสุทธิ = paid * (100 - used) * 7 / 800
    # ใช้จำนวนเต็มล้วนเพื่อหลีกเลี่ยงความคลาดเคลื่อนของทศนิยม
    if restock:
        return paid * (100 - used_percent) * 7 // 800
    return paid * (100 - used_percent) // 100
