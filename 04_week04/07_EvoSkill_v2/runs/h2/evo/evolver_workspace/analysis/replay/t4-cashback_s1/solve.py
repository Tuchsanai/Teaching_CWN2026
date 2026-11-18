"""BaanKafe cashback calculator.

ยอดซื้อ (amount) และเงินคืนทั้งหมดเป็น "สตางค์" (1 บาท = 100 สตางค์)
คำนวณด้วยจำนวนเต็มล้วน (basis points) เพื่อหลีกเลี่ยงความคลาดเคลื่อนของ float
และปัดเศษลง (floor) เป็นจำนวนเต็มสตางค์
"""

# อัตราเงินคืนหน่วยเป็น basis points (1 bp = 0.01%)
# silver 1.5% = 150 bp, gold 2.5% = 250 bp, platinum 4% = 400 bp
RATE_BP = {
    "silver": 150,
    "gold": 250,
    "platinum": 400,
}

MIN_AMOUNT = 100 * 100        # ยอดซื้อขั้นต่ำ 100 บาท = 10,000 สตางค์
MAX_CASHBACK = 200 * 100      # เงินคืนสูงสุดต่อบิล 200 บาท = 20,000 สตางค์
BIRTHDAY_MULTIPLIER = 2       # ซื้อในเดือนเกิดได้ 2 เท่า
BP_DIVISOR = 10_000


def cashback(amount: int, tier: str, birthday: bool = False) -> int:
    """คืนจำนวนเงินคืนสมาชิก (สตางค์, จำนวนเต็ม)

    amount   : ยอดซื้อ หน่วยสตางค์ (>= 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    key = str(tier).strip().lower()
    if key not in RATE_BP:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r} (ต้องเป็น silver, gold หรือ platinum)")

    # ยอดซื้อต่ำกว่า 100 บาท ไม่ได้เงินคืน
    if amount < MIN_AMOUNT:
        return 0

    cb = amount * RATE_BP[key] // BP_DIVISOR

    if birthday:
        cb *= BIRTHDAY_MULTIPLIER

    return min(cb, MAX_CASHBACK)


if __name__ == "__main__":
    # ตัวอย่างและการทดสอบพื้นฐาน
    assert cashback(9_999, "platinum") == 0          # ต่ำกว่า 100 บาท
    assert cashback(10_000, "silver") == 150         # 100 บาท * 1.5% = 1.50 บาท
    assert cashback(10_000, "silver", True) == 300   # เดือนเกิด 2 เท่า
    assert cashback(10_000, "gold") == 250           # 100 บาท * 2.5%
    assert cashback(10_000, "platinum") == 400       # 100 บาท * 4%
    assert cashback(100_000, "platinum") == 4_000    # 1,000 บาท * 4% = 40 บาท
    assert cashback(1_000_000, "platinum") == 20_000 # 4% = 400 บาท -> ถูกจำกัดที่ 200 บาท
    assert cashback(1_000_000, "platinum", True) == 20_000  # เดือนเกิดก็ยังไม่เกิน 200 บาท
    assert cashback(10_001, "gold") == 250           # 100.01 บาท * 2.5% = 2.500025 -> ปัดลง 250
    assert cashback(7_000, "gold", True) == 0        # ต่ำกว่าขั้นต่ำ ไม่ได้รับแม้เดือนเกิด
    assert cashback(0, "gold") == 0
    print("ทุกการทดสอบผ่าน")
