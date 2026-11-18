"""คำนวณเงินคืนสมาชิกของร้าน BaanKafe

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม). ไม่มี side effect ตอน import.

ลำดับการคำนวณ (ปัดครั้งเดียวตอนท้าย):
  1. ตรวจ input ทั้งหมด (ผิดชนิดหรือนอกช่วง -> ValueError)
  2. ยอดต่ำกว่า 100 บาท -> 0
  3. ยอด x อัตราตาม tier (exact ด้วย Fraction)
  4. เดือนเกิด -> คูณ 2
  5. เพดาน 200 บาทต่อบิล
  6. ปัดลงเป็นจำนวนเต็มสตางค์ (เงินที่ร้านจ่ายออกให้ลูกค้า)
"""
import math
from fractions import Fraction

# อัตราเงินคืนต่อยอดซื้อ (ใช้ Fraction ไม่ใช้ float)
RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(40, 1000),  # 4%
}
MIN_AMOUNT = 10000       # ยอดขั้นต่ำ 100 บาท (ต่ำกว่านี้ไม่ได้เงินคืน)
MAX_CASHBACK = 20000     # เงินคืนสูงสุดต่อบิล 200 บาท
BIRTHDAY_MULTIPLIER = 2  # ซื้อในเดือนเกิดได้ 2 เท่า


def cashback(amount, tier, birthday):
    """คืนจำนวนเงินคืนเป็นสตางค์ (จำนวนเต็ม)

    amount   : ยอดซื้อ หน่วยสตางค์ จำนวนเต็ม >= 0
    tier     : "silver" | "gold" | "platinum" (ตัวพิมพ์เล็กเท่านั้น)
    birthday : True ถ้าซื้อในเดือนเกิด, False ถ้าไม่ใช่
    """
    # ตรวจ input ก่อนทุกอย่าง (รวมถึงเงื่อนไขยอดขั้นต่ำ)
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่น้อยกว่า 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError(f"tier ต้องเป็นหนึ่งใน {sorted(RATES)}")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    # เงื่อนไขธุรกิจ
    if amount < MIN_AMOUNT:
        return 0

    value = Fraction(amount) * RATES[tier]
    if birthday:
        value *= BIRTHDAY_MULTIPLIER
    value = min(value, MAX_CASHBACK)
    return math.floor(value)


if __name__ == "__main__":
    print(cashback(10000, "silver", False))   # 150
    print(cashback(10000, "platinum", True))  # 800
    print(cashback(1000000, "gold", False))   # 20000
