"""BaanKafe cashback. หน่วยเงิน = สตางค์ (จำนวนเต็ม)

ข้อสันนิษฐานที่โจทย์ไม่ได้ระบุ (ตาม house-rules):
- เงินคืนเป็นเงินที่ร้านจ่ายออก -> ปัดทิ้ง (floor) ครั้งเดียวตอนท้าย แล้วค่อยใช้เพดาน
- ตรวจ input ก่อน early-return ทุกครั้ง
ข้อที่ขัดกับโจทย์ (silver ไม่ได้ x2 ในเดือนเกิด) ไม่ใช้ เพราะโจทย์ระบุว่าเดือนเกิดได้ 2 เท่า
ไม่มีข้อยกเว้น -> ทุก tier ได้ x2
"""
from fractions import Fraction

RATES = {
    "silver": Fraction(15, 1000),
    "gold": Fraction(25, 1000),
    "platinum": Fraction(4, 100),
}
MIN_AMOUNT = 100 * 100   # 100 บาท
CAP = 200 * 100          # 200 บาท


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount ต้องเป็นจำนวนเต็มตั้งแต่ 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    if amount < MIN_AMOUNT:
        return 0
    value = amount * RATES[tier]
    if birthday:
        value *= 2
    return min(CAP, int(value // 1))
