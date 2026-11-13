"""คำนวณเงินคืนสมาชิกร้าน BaanKafe

หน่วยของ amount เป็นสตางค์ (จำนวนเต็มตั้งแต่ 0)
ผลลัพธ์เป็นจำนวนเต็มสตางค์
"""

from decimal import Decimal, ROUND_DOWN

MIN_AMOUNT = 100 * 100          # 100 บาท = 10000 สตางค์ (ยอดต่ำกว่านี้ไม่ได้เงินคืน)
MAX_CASHBACK = 200 * 100        # เงินคืนสูงสุด 200 บาท = 20000 สตางค์ ต่อบิล
BIRTHDAY_MULTIPLIER = 2         # เดือนเกิดได้เงินคืน 2 เท่า

RATES = {
    "silver": Decimal("0.015"),    # 1.5%
    "gold": Decimal("0.025"),      # 2.5%
    "platinum": Decimal("0.04"),   # 4%
}


def cashback(amount: int, tier: str, birthday: bool) -> int:
    """คืนจำนวนเงินคืน (สตางค์, จำนวนเต็ม)

    - amount: ยอดซื้อ (สตางค์) ต้องไม่ติดลบ
    - tier: "silver" | "gold" | "platinum"
    - birthday: True ถ้าซื้อในเดือนเกิด (ได้ 2 เท่า)
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if tier not in RATES:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r}")

    if amount < MIN_AMOUNT:
        return 0

    # คำนวณด้วย Decimal เพื่อไม่ให้เกิดความคลาดเคลื่อนจากทศนิยม
    # ปัดลง (ROUND_DOWN) ให้เป็นจำนวนเต็มสตางค์
    value = (Decimal(amount) * RATES[tier]).to_integral_value(rounding=ROUND_DOWN)
    result = int(value)

    if birthday:
        result *= BIRTHDAY_MULTIPLIER

    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    # ตัวอย่างการใช้งานและการทดสอบเบื้องต้น
    assert cashback(9999, "gold", False) == 0          # ต่ำกว่า 100 บาท
    assert cashback(10000, "silver", False) == 150     # 100 บาท * 1.5% = 1.5 บาท
    assert cashback(10000, "silver", True) == 300      # เดือนเกิด 2 เท่า
    assert cashback(100000, "gold", False) == 2500     # 1000 บาท * 2.5% = 25 บาท
    assert cashback(1000000, "platinum", False) == 20000  # 40,000 สตางค์ ถูกจำกัดที่ 200 บาท
    assert cashback(1000000, "silver", True) == 20000  # 15,000 * 2 = 30,000 ถูกจำกัดที่ 20,000
    assert cashback(5000000, "platinum", True) == 20000
    assert cashback(12345, "gold", False) == 308       # 12345 * 2.5% = 308.625 → 308
    print("ทดสอบผ่านทั้งหมด")
