"""BaanKafe: คำนวณเงินคืนสำหรับคอร์สสอนชงกาแฟ

กติกา
- paid         : เงินที่ลูกค้าจ่าย (สตางค์ จำนวนเต็ม >= 0)
- used_percent : เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0–100)
- restock      : True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
- คืนตามสัดส่วนที่ยังไม่ได้เรียน
- เรียนไปแล้วเกิน 80% ไม่คืนเงิน (80% พอดียังคืน)
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ ปัดเศษลง (ไม่จ่ายเกินให้ลูกค้า)
"""


def refund(paid: int, used_percent: int, restock: bool) -> int:
    if not isinstance(paid, int) or isinstance(paid, bool) or paid < 0:
        raise ValueError("paid ต้องเป็นจำนวนเต็มสตางค์ที่ >= 0")
    if not isinstance(used_percent, int) or isinstance(used_percent, bool) \
            or not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็มระหว่าง 0 ถึง 100")

    if used_percent > 80:
        return 0

    # ยอดคืนก่อนหักค่าดำเนินการ = paid * (100 - used_percent) / 100
    # ค่าดำเนินการ 12.5% (= 1/8) ของยอดนั้น ดังนั้นยอดสุทธิ = ยอดคืน * 7/8
    #   = paid * (100 - used_percent) * 7 / 800
    # ใช้จำนวนเต็มทั้งหมดเพื่อหลีกเลี่ยงข้อผิดพลาดจากทศนิยม
    remaining = paid * (100 - used_percent)
    if restock:
        return remaining * 7 // 800
    return remaining // 100
