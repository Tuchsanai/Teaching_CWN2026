"""BaanKafe cashback calculator.

ยอดทั้งหมดคิดเป็นสตางค์ (จำนวนเต็ม) เพื่อหลีกเลี่ยงปัญหาทศนิยมของ float
"""

MIN_AMOUNT = 100 * 100          # ยอดซื้อขั้นต่ำที่ได้เงินคืน: 100 บาท = 10,000 สตางค์
MAX_CASHBACK = 200 * 100        # เงินคืนสูงสุดต่อบิล: 200 บาท = 20,000 สตางค์
BIRTHDAY_MULTIPLIER = 2         # เดือนเกิดได้เงินคืน 2 เท่า

# อัตราเงินคืนเป็นเศษส่วนของจำนวนเต็ม: rate = num / den
# silver 1.5% = 15/1000, gold 2.5% = 25/1000, platinum 4% = 40/1000
RATES = {
    "silver": (15, 1000),
    "gold": (25, 1000),
    "platinum": (40, 1000),
}


def cashback(amount, tier, birthday):
    """คืนค่าเงินคืนเป็นจำนวนเต็มสตางค์

    amount   : ยอดซื้อ (สตางค์, จำนวนเต็มตั้งแต่ 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    key = tier.strip().lower() if isinstance(tier, str) else tier
    if key not in RATES:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r}")

    if amount < MIN_AMOUNT:
        return 0

    num, den = RATES[key]
    result = amount * num // den            # ปัดลง (floor) เป็นจำนวนเต็มสตางค์
    if birthday:
        result *= BIRTHDAY_MULTIPLIER
    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    # ตัวอย่างการตรวจสอบเบื้องต้น
    assert cashback(9999, "platinum", True) == 0          # ต่ำกว่า 100 บาท
    assert cashback(10000, "silver", False) == 150        # 100 บาท × 1.5%
    assert cashback(10000, "silver", True) == 300         # เดือนเกิด 2 เท่า
    assert cashback(10000, "gold", False) == 250          # 100 บาท × 2.5%
    assert cashback(10000, "platinum", False) == 400      # 100 บาท × 4%
    assert cashback(1000000, "platinum", False) == 20000  # 4% = 400 บาท -> ถูกจำกัดที่ 200 บาท
    assert cashback(1000000, "gold", True) == 20000       # 5% = 500 บาท -> ถูกจำกัดที่ 200 บาท
    assert cashback(500000, "silver", False) == 7500      # 5,000 บาท × 1.5% = 75 บาท
    assert cashback(500000, "silver", True) == 15000      # เดือนเกิด 150 บาท
    assert cashback(0, "gold", True) == 0
    print("ทดสอบผ่านทั้งหมด")
