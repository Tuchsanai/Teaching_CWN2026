from fractions import Fraction

# อัตราเงินคืน (ตัวคูณ) ของแต่ละ tier
RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(40, 1000),  # 4%
}

MIN_AMOUNT = 10_000       # 100 บาท (สตางค์)
MAX_CASHBACK = 20_000     # 200 บาทต่อบิล (สตางค์)
BIRTHDAY_MULTIPLIER = 2   # เดือนเกิดได้ 2 เท่า


def cashback(amount, tier, birthday):
    """คำนวณเงินคืนสมาชิกของ BaanKafe เป็นสตางค์ (จำนวนเต็ม)

    amount   : ยอดซื้อเป็นสตางค์ (int, >= 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด (bool)
    """
    # ตรวจ input ก่อนคำนวณ ปฏิเสธชนิดผิดด้วย ValueError
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่น้อยกว่า 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError(f"tier ต้องเป็นหนึ่งใน {sorted(RATES)}")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    # ยอดต่ำกว่า 100 บาท ไม่ได้เงินคืน
    if amount < MIN_AMOUNT:
        return 0

    # คูณทุกตัวคูณก่อน แล้วค่อยปัดลงครั้งเดียว (ร้านจ่ายออก จึงปัดลง)
    value = Fraction(amount) * RATES[tier]
    if birthday:
        value *= BIRTHDAY_MULTIPLIER
    result = int(value // 1)

    # เพดานต่อบิล ใช้หลังคูณทั้งหมดแล้ว
    return min(result, MAX_CASHBACK)
