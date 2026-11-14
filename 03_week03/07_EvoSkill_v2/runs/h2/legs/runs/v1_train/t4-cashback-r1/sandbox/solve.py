"""cashback(amount, tier, birthday) — คิดเงินคืนสมาชิก BaanKafe

หน่วย: amount และผลลัพธ์เป็นสตางค์ (จำนวนเต็ม) คำนวณด้วย Fraction ปัดครั้งเดียวที่ขั้นสุดท้าย

ลำดับการคิด:
1. ยอดต่ำกว่า 100 บาท (10000 สตางค์) -> ไม่ได้เงินคืน (0)
2. เงินคืนดิบ = ยอด x อัตราตามระดับ (silver 1.5%, gold 2.5%, platinum 4%)
3. ซื้อในเดือนเกิด (birthday=True) -> คูณ 2
4. ตัดเพดาน 200 บาท (20000 สตางค์) ต่อบิล หลังคูณ 2 แล้ว
5. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ที่ขั้นสุดท้าย

ตัวเลือกการตีความ (เปลี่ยนได้ที่ค่าคงที่ด้านล่าง หรือบรรทัดปัดเศษ):
- เกณฑ์ขั้นต่ำตรวจจากยอดซื้อก่อนคำนวณ (ยอด = 10000 ได้เงินคืน)
- เพดานนับหลังคูณ 2 (เดือนเกิดได้สูงสุด 200 บาทเหมือนกัน)
- โหมดปัดเป็นปัดครึ่งขึ้น ถ้าต้องการปัดลง ให้เปลี่ยนเป็น math.floor(capped)
"""
from fractions import Fraction
import math

MIN_AMOUNT = 10000    # 100 บาท ยอดขั้นต่ำที่ได้เงินคืน (สตางค์)
MAX_CASHBACK = 20000  # 200 บาท เพดานต่อบิล (สตางค์)

RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(40, 1000),  # 4%
}


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็มสตางค์")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if tier not in RATES:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")

    # 1. เกณฑ์ขั้นต่ำ
    if amount < MIN_AMOUNT:
        return 0

    # 2. อัตราตามระดับ
    raw = Fraction(amount) * RATES[tier]

    # 3. เดือนเกิดได้ 2 เท่า
    if birthday:
        raw *= 2

    # 4. เพดานต่อบิล
    capped = min(raw, Fraction(MAX_CASHBACK))

    # 5. ปัดครึ่งขึ้นเป็นสตางค์ (ค่าไม่ติดลบ)
    return math.floor(capped + Fraction(1, 2))
