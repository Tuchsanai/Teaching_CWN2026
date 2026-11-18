"""BaanKafe cashback calculator.

amount   : ยอดซื้อเป็นสตางค์ (จำนวนเต็ม >= 0)
tier     : "silver" | "gold" | "platinum"
birthday : True = ซื้อในเดือนเกิด (ได้เงินคืน 2 เท่า)

ผลลัพธ์เป็นจำนวนเต็มสตางค์
"""

# อัตราเงินคืนในหน่วย basis point (1 bp = 0.01%) เพื่อหลีกเลี่ยง float
RATE_BP = {
    "silver": 150,    # 1.5%
    "gold": 250,      # 2.5%
    "platinum": 400,  # 4%
}

MIN_AMOUNT = 100 * 100        # 100 บาท = 10,000 สตางค์
MAX_CASHBACK = 200 * 100      # เพดาน 200 บาท = 20,000 สตางค์ ต่อบิล
BIRTHDAY_MULTIPLIER = 2
BP_DENOMINATOR = 10_000


def cashback(amount: int, tier: str, birthday: bool = False) -> int:
    """คำนวณเงินคืนของบิลหนึ่งใบ (หน่วยสตางค์, จำนวนเต็ม)."""
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    key = str(tier).strip().lower()
    if key not in RATE_BP:
        raise ValueError(f"ไม่รู้จักระดับสมาชิก: {tier!r}")

    # ยอดต่ำกว่า 100 บาท ไม่ได้เงินคืน
    if amount < MIN_AMOUNT:
        return 0

    # ปัดลง (floor) เป็นจำนวนเต็มสตางค์
    result = amount * RATE_BP[key] // BP_DENOMINATOR

    # เดือนเกิด ได้ 2 เท่า
    if birthday:
        result *= BIRTHDAY_MULTIPLIER

    # เพดานต่อบิล 200 บาท
    return min(result, MAX_CASHBACK)
