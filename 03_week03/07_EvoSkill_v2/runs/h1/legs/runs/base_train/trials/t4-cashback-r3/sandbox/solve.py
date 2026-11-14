"""BaanKafe cashback calculator.

All money values are integers in satang (1 baht = 100 satang).
Rates are expressed in basis points (1 bp = 0.01%) so the math stays exact.
"""

MIN_PURCHASE = 100 * 100          # 100 บาท ขึ้นไปจึงจะได้เงินคืน (satang)
MAX_CASHBACK = 200 * 100          # เงินคืนสูงสุดต่อบิล 200 บาท (satang)
BIRTHDAY_MULTIPLIER = 2           # เดือนเกิด ได้ 2 เท่า

# อัตราเงินคืนของแต่ละระดับสมาชิก (basis points: 150 = 1.5%)
TIER_RATE_BP = {
    "silver": 150,     # 1.5%
    "gold": 250,       # 2.5%
    "platinum": 400,   # 4%
}


def cashback(amount: int, tier: str, birthday: bool = False) -> int:
    """คำนวณเงินคืนสมาชิกของ BaanKafe ผลลัพธ์เป็นจำนวนเต็มสตางค์

    Args:
        amount: ยอดซื้อ หน่วยสตางค์ (จำนวนเต็ม >= 0)
        tier: "silver", "gold" หรือ "platinum"
        birthday: True หากซื้อในเดือนเกิด

    Returns:
        เงินคืนเป็นสตางค์ (จำนวนเต็ม)

    Raises:
        TypeError: amount ไม่ใช่จำนวนเต็ม
        ValueError: amount ติดลบ หรือ tier ไม่ถูกต้อง
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    key = tier.strip().lower() if isinstance(tier, str) else None
    if key not in TIER_RATE_BP:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r} (ต้องเป็น silver, gold หรือ platinum)")

    # ยอดซื้อต่ำกว่า 100 บาท ไม่ได้เงินคืน
    if amount < MIN_PURCHASE:
        return 0

    # ปัดลง (floor) เป็นสตางค์ เพื่อไม่จ่ายเกินสิทธิ์
    result = amount * TIER_RATE_BP[key] // 10_000

    # เดือนเกิดได้ 2 เท่า
    if birthday:
        result *= BIRTHDAY_MULTIPLIER

    # จำกัดเงินคืนสูงสุดต่อบิล (ใช้หลังคูณเดือนเกิดแล้ว)
    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    # ตัวอย่างการใช้งานและกรณีทดสอบเบื้องต้น
    cases = [
        (9_999, "gold", False, 0),          # ต่ำกว่า 100 บาท
        (10_000, "silver", False, 150),     # 100 บาท * 1.5% = 1.50 บาท
        (10_000, "gold", True, 500),        # 100 บาท * 2.5% * 2 = 5 บาท
        (100_000, "platinum", False, 4_000),  # 1,000 บาท * 4% = 40 บาท
        (1_000_000, "platinum", False, 20_000),  # 40,000 สตางค์ ถูกจำกัดที่ 200 บาท
        (1_000_000, "silver", True, 20_000),     # 15,000 * 2 = 30,000 -> cap 20,000
        (3_333, "silver", False, 0),
        (33_333, "silver", False, 499),     # ปัดลง
    ]
    for amount, tier, bday, expected in cases:
        got = cashback(amount, tier, bday)
        status = "OK " if got == expected else "FAIL"
        print(f"{status} cashback({amount}, {tier!r}, {bday}) = {got} (expected {expected})")
