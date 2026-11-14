"""BaanKafe: คำนวณเงินคืนของคอร์สสอนชงกาแฟ

กติกา
- paid: เงินที่ลูกค้าจ่ายมา (สตางค์, จำนวนเต็ม >= 0)
- used_percent: เรียนไปแล้วกี่เปอร์เซ็นต์ (จำนวนเต็ม 0-100)
- restock: True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน, False = ไม่หัก
- คืนตามสัดส่วนที่ยังไม่ได้เรียน (100 - used_percent)%
- เรียนไปแล้วเกิน 80% ไม่คืนเงิน (คืน 0)
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดทิ้งเศษสตางค์ลง)
"""


def refund(paid: int, used_percent: int, restock: bool) -> int:
    """คืนจำนวนเงิน (สตางค์, จำนวนเต็ม) ที่ต้องคืนให้ลูกค้า"""
    if isinstance(paid, bool) or not isinstance(paid, int):
        raise ValueError("paid ต้องเป็นจำนวนเต็ม (สตางค์)")
    if paid < 0:
        raise ValueError("paid ต้องไม่ติดลบ")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int):
        raise ValueError("used_percent ต้องเป็นจำนวนเต็ม")
    if not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องอยู่ระหว่าง 0 ถึง 100")

    # เรียนเกิน 80% แล้ว ไม่คืนเงิน
    if used_percent > 80:
        return 0

    # ใช้จำนวนเต็มล้วน เพื่อไม่ให้เกิดความคลาดเคลื่อนจากทศนิยม
    # ยอดคืนก่อนหักค่าดำเนินการ = paid * (100 - used) / 100
    # หักค่าดำเนินการ 12.5% (= 1/8) -> ยอดคงเหลือ = 7/8 ของยอดคืน
    # รวมเป็น paid * (100 - used) * 7 / 800   (ถ้า restock)
    #      หรือ paid * (100 - used) * 8 / 800 = paid * (100 - used) / 100   (ถ้าไม่ restock)
    factor = 7 if restock else 8
    return paid * (100 - used_percent) * factor // 800
