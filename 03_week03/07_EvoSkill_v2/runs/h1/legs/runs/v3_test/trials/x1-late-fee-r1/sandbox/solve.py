from fractions import Fraction


def _require_int(value, name, low, high):
    # ปฏิเสธ bool, float, str, None ทั้งหมด (ไม่แปลงค่า)
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if value < low or value > high:
        raise ValueError(f"{name} ต้องอยู่ในช่วง {low}–{high}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int, x ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def late_fee(amount, days_late):
    """คืนค่าปรับ (สตางค์, int) สำหรับยอดค้างชำระที่ชำระช้า

    amount    : ยอดค้างชำระ (สตางค์) จำนวนเต็ม >= 0
    days_late : จำนวนวันที่ช้า จำนวนเต็ม 0–365
    - ช้าไม่เกิน 3 วัน ไม่มีค่าปรับ
    - ช้าเกิน 3 วัน คิด 0.75% ต่อวัน นับทุกวัน (รวม 3 วันแรก)
    - ค่าปรับสูงสุด 15% ของยอดค้างชำระ
    - ปัดครึ่งขึ้นครั้งเดียวตอนท้าย (ลูกค้าจ่ายให้ร้าน)
    """
    amount = _require_int(amount, "amount", 0, 10**18)
    days_late = _require_int(days_late, "days_late", 0, 365)

    if days_late <= 3:
        return 0

    fee = Fraction(amount) * Fraction(3, 400) * days_late   # 0.75% = 3/400
    cap = Fraction(amount) * Fraction(15, 100)              # 15%
    return _half_up(min(fee, cap))
