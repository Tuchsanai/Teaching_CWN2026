"""BaanKafe member cashback calculator.

Units: amounts are in satang (1 baht = 100 satang).
"""

# อัตราเงินคืนหน่วยเป็น basis point (1 bp = 0.01%) เพื่อใช้จำนวนเต็มล้วน
# silver 1.5% = 150 bp, gold 2.5% = 250 bp, platinum 4% = 400 bp
RATE_BP = {
    "silver": 150,
    "gold": 250,
    "platinum": 400,
}

MIN_AMOUNT = 100 * 100      # 100 บาท ในหน่วยสตางค์
MAX_CASHBACK = 200 * 100    # 200 บาท ต่อบิล ในหน่วยสตางค์
BIRTHDAY_MULTIPLIER = 2


def cashback(amount: int, tier: str, birthday: bool) -> int:
    """คำนวณเงินคืนสมาชิก (หน่วยสตางค์, จำนวนเต็ม)

    - amount: ยอดซื้อ (สตางค์, >= 0)
    - tier: "silver" | "gold" | "platinum"
    - birthday: True ถ้าซื้อในเดือนเกิด (ได้เงินคืนเป็น 2 เท่า)

    กติกา: ยอดต่ำกว่า 100 บาท ไม่ได้เงินคืน, คิดตามอัตรา tier,
    เดือนเกิดคูณ 2, แล้วจำกัดไม่เกิน 200 บาทต่อบิล, ปัดเศษทิ้ง (floor).
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if tier not in RATE_BP:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r}")

    if amount < MIN_AMOUNT:
        return 0

    result = amount * RATE_BP[tier] // 10000
    if birthday:
        result *= BIRTHDAY_MULTIPLIER
    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(cashback(10000, "silver", False))   # 100 บาท -> 1.50 บาท = 150
    print(cashback(10000, "silver", True))    # เดือนเกิด -> 300
    print(cashback(9999, "platinum", True))   # ต่ำกว่า 100 บาท -> 0
    print(cashback(1000000, "platinum", True))  # 10,000 บาท -> cap 20000
