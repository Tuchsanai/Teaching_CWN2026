"""BaanKafe cashback calculator.

หน่วยทั้งหมดเป็นสตางค์ (satang) และคำนวณด้วยจำนวนเต็มล้วน เพื่อไม่ให้เกิดปัญหาทศนิยม
"""

# อัตราเงินคืนเป็น basis point (1 bp = 0.01%) เช่น 150 bp = 1.5%
RATE_BP = {
    "silver": 150,    # 1.5%
    "gold": 250,      # 2.5%
    "platinum": 400,  # 4%
}

MIN_PURCHASE = 100 * 100      # 100 บาท = 10,000 สตางค์
MAX_CASHBACK = 200 * 100      # 200 บาท = 20,000 สตางค์ ต่อบิล
BIRTHDAY_MULTIPLIER = 2
BP_DENOMINATOR = 10_000


def cashback(amount, tier, birthday=False):
    """คืนค่าเงินคืนเป็นสตางค์ (จำนวนเต็ม)

    amount   : ยอดซื้อเป็นสตางค์ (จำนวนเต็ม >= 0)
    tier     : "silver", "gold" หรือ "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด (ได้เงินคืน 2 เท่า)
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if tier not in RATE_BP:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r} (ต้องเป็น silver, gold หรือ platinum)")

    # ยอดซื้อต่ำกว่า 100 บาท ไม่ได้เงินคืน
    if amount < MIN_PURCHASE:
        return 0

    # คิดเงินคืนแบบปัดลง (floor) เป็นจำนวนเต็มสตางค์
    result = amount * RATE_BP[tier] // BP_DENOMINATOR

    # เดือนเกิดได้ 2 เท่า
    if birthday:
        result *= BIRTHDAY_MULTIPLIER

    # เพดานสูงสุด 200 บาทต่อบิล (ใช้หลังคูณเดือนเกิด)
    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    # ตัวอย่างการใช้งานและการตรวจสอบเบื้องต้น
    assert cashback(9_999, "gold") == 0            # ต่ำกว่า 100 บาท
    assert cashback(10_000, "silver") == 150       # 100 บาท * 1.5% = 1.50 บาท
    assert cashback(10_000, "silver", True) == 300 # เดือนเกิด 2 เท่า
    assert cashback(10_000, "gold") == 250         # 2.5%
    assert cashback(10_000, "platinum") == 400     # 4%
    assert cashback(1_000_000, "platinum") == 20_000   # ถึงเพดาน 200 บาท
    assert cashback(1_000_000, "platinum", True) == 20_000  # เพดานยังคงอยู่หลังคูณ
    assert cashback(7_777, "gold", False) == 0     # ยังต่ำกว่า 100 บาท
    assert cashback(5_000_00, "gold") == 12_500    # 5,000 บาท * 2.5% = 125 บาท
    print("ทดสอบผ่านทั้งหมด")
