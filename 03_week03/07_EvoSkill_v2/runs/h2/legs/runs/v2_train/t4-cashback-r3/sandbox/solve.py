from fractions import Fraction

# หน่วยทั้งหมดเป็นสตางค์ (1 บาท = 100 สตางค์)
MIN_PURCHASE = 100 * 100      # ยอดซื้อขั้นต่ำ 100 บาท
MAX_CASHBACK = 200 * 100      # เงินคืนสูงสุด 200 บาทต่อบิล
BIRTHDAY_MULTIPLIER = 2       # เดือนเกิดได้ 2 เท่า

# อัตราเงินคืน (เปอร์เซ็นต์)
RATES = {
    "silver": 1.5,
    "gold": 2.5,
    "platinum": 4,
}


def cashback(amount, tier, birthday):
    """คำนวณเงินคืนสมาชิกของร้าน BaanKafe เป็นจำนวนเต็มสตางค์

    ลำดับการคิด:
      1. ตรวจยอดซื้อขั้นต่ำ (ต่ำกว่า 100 บาท ไม่ได้เงินคืน) ด้วยยอดตั้งต้น
      2. คิดเงินคืน = ยอด × อัตรา% (เก็บเป็น Fraction ไม่ปัดระหว่างทาง)
      3. ถ้าเป็นเดือนเกิด คูณ 2
      4. ปัดลง (ตัดเศษสตางค์ทิ้ง) ที่ขั้นสุดท้าย เพราะโจทย์ไม่ได้ระบุการปัด
      5. ตัดเพดาน 200 บาทต่อบิลที่ขั้นสุดท้าย
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if tier not in RATES:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r} (ต้องเป็น silver, gold หรือ platinum)")

    # 1. ยอดซื้อต่ำกว่า 100 บาท ไม่ได้เงินคืน
    if amount < MIN_PURCHASE:
        return 0

    # 2. อัตราเป็นเศษส่วนเพื่อความแม่นยำ
    cashback_amount = Fraction(amount) * Fraction(RATES[tier]) / 100

    # 3. เดือนเกิดได้ 2 เท่า
    if birthday:
        cashback_amount *= BIRTHDAY_MULTIPLIER

    # 4. ปัดลงเป็นจำนวนเต็มสตางค์
    cashback_satang = int(cashback_amount)  # ค่าไม่ติดลบ int() = floor

    # 5. เพดานต่อบิล
    return min(cashback_satang, MAX_CASHBACK)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน (หน่วยสตางค์)
    print(cashback(10000, "silver", False))    # 100 บาท -> 150 สตางค์
    print(cashback(50000, "gold", True))       # 500 บาท, 2.5%, เดือนเกิด -> 2500 สตางค์
    print(cashback(50000, "platinum", True))   # 500 บาท, 4%, เดือนเกิด -> 4000 สตางค์ (ไม่ชนเพดาน)
    print(cashback(100000, "platinum", True))  # 1000 บาท, 4%, เดือนเกิด -> 8000 สตางค์ (ไม่ชนเพดาน)
    print(cashback(1000000, "platinum", True)) # 10000 บาท, 4%, เดือนเกิด -> 800 บาท ถูกตัดเหลือ 20000 สตางค์
