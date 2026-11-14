"""BaanKafe cashback calculator.

ทุกค่าเงินเป็นสตางค์ (satang) และคำนวณด้วยจำนวนเต็มทั้งหมด เพื่อไม่ให้เกิดปัญหาทศนิยมจาก float
"""

MIN_AMOUNT = 100 * 100          # ยอดซื้อขั้นต่ำที่ได้เงินคืน: 100 บาท = 10,000 สตางค์
MAX_CASHBACK = 200 * 100        # เงินคืนสูงสุดต่อบิล: 200 บาท = 20,000 สตางค์
BIRTHDAY_MULTIPLIER = 2         # ซื้อในเดือนเกิดได้เงินคืน 2 เท่า

# อัตราเงินคืนเป็นเศษส่วน (ตัวเศษ, ตัวส่วน) เพื่อหลีกเลี่ยง float
# silver 1.5% = 15/1000, gold 2.5% = 25/1000, platinum 4% = 40/1000
RATES = {
    "silver": (15, 1000),
    "gold": (25, 1000),
    "platinum": (40, 1000),
}


def cashback(amount: int, tier: str, birthday: bool) -> int:
    """คืนจำนวนเงินคืนสมาชิกเป็นสตางค์ (จำนวนเต็ม)

    amount   : ยอดซื้อ หน่วยสตางค์ (>= 0)
    tier     : "silver", "gold" หรือ "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    key = tier.strip().lower() if isinstance(tier, str) else tier
    if key not in RATES:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r} (ต้องเป็น silver, gold หรือ platinum)")

    if amount < MIN_AMOUNT:
        return 0

    num, den = RATES[key]
    result = amount * num // den          # ปัดลงเป็นจำนวนเต็มสตางค์

    if birthday:
        result *= BIRTHDAY_MULTIPLIER

    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(cashback(10_000, "silver", False))    # 150  (100 บาท × 1.5%)
    print(cashback(10_000, "silver", True))     # 300  (เดือนเกิด 2 เท่า)
    print(cashback(9_999, "platinum", False))   # 0    (ต่ำกว่า 100 บาท)
    print(cashback(1_000_000, "gold", False))   # 20000 (25,000 ถูกจำกัดที่ 200 บาท)
    print(cashback(1_000_000, "platinum", True))  # 20000 (ถูกจำกัดที่ 200 บาท)
