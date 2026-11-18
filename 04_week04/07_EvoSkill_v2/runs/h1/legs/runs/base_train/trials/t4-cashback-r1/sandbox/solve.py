"""BaanKafe cashback calculator.

ยอดเงินทั้งหมดเป็นสตางค์ (จำนวนเต็ม) และผลลัพธ์ก็เป็นสตางค์ (จำนวนเต็ม)
"""

# อัตราเงินคืน เก็บเป็น basis points (1 bp = 0.01%) เพื่อหลีกเลี่ยงเลขทศนิยม
# silver 1.5% = 150 bp, gold 2.5% = 250 bp, platinum 4% = 400 bp
_RATE_BP = {
    "silver": 150,
    "gold": 250,
    "platinum": 400,
}

_MIN_AMOUNT = 100 * 100      # 100 บาท = 10,000 สตางค์ (ต่ำกว่านี้ไม่ได้เงินคืน)
_BIRTHDAY_MULTIPLIER = 2     # เดือนเกิดได้เงินคืน 2 เท่า
_MAX_CASHBACK = 200 * 100    # เงินคืนสูงสุด 200 บาท = 20,000 สตางค์ต่อบิล
_BP_DENOMINATOR = 10_000


def cashback(amount: int, tier: str, birthday: bool) -> int:
    """คำนวณเงินคืนสมาชิกของ BaanKafe เป็นสตางค์ (จำนวนเต็ม)

    amount   : ยอดซื้อ หน่วยสตางค์ (>= 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด (เงินคืนเป็น 2 เท่า)
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    key = tier.strip().lower() if isinstance(tier, str) else tier
    if key not in _RATE_BP:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r} (ต้องเป็น silver, gold หรือ platinum)")

    if amount < _MIN_AMOUNT:
        return 0

    cb = amount * _RATE_BP[key] // _BP_DENOMINATOR   # ปัดลง (floor) เป็นสตางค์
    if birthday:
        cb *= _BIRTHDAY_MULTIPLIER

    return min(cb, _MAX_CASHBACK)
