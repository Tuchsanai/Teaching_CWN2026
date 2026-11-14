"""คำนวณเงินคืนคอร์สสอนชงกาแฟของ BaanKafe."""


def refund(paid: int, used_percent: int, restock: bool) -> int:
    """คืนยอดเงินที่ต้องคืนลูกค้า (หน่วยเป็นสตางค์ จำนวนเต็ม)

    paid          -- เงินที่ลูกค้าจ่ายมา (สตางค์, >= 0)
    used_percent  -- เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock       -- True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน

    กติกา:
      - เรียนไปแล้วเกิน 80% ไม่คืนเงิน (คืน 0)
      - คืนตามสัดส่วนที่ยังไม่ได้เรียน: paid * (100 - used_percent) / 100
      - ถ้า restock=True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน (คงเหลือ 87.5%)
      - ผลลัพธ์ปัดลงเป็นจำนวนเต็มสตางค์ (คำนวณด้วยจำนวนเต็มล้วน ไม่มีค่าคลาดเคลื่อนจากทศนิยม)
    """
    if isinstance(paid, bool) or not isinstance(paid, int) or paid < 0:
        raise ValueError("paid ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int) \
            or not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็มตั้งแต่ 0 ถึง 100")

    if used_percent > 80:
        return 0

    remaining = 100 - used_percent
    if restock:
        # paid * remaining / 100 * (1 - 12.5%) = paid * remaining * 7 / 800
        return paid * remaining * 7 // 800
    return paid * remaining // 100
