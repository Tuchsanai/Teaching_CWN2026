"""ฟังก์ชันคิดเงินคืนสมาชิกของร้าน BaanKafe."""

# อัตราเงินคืนเก็บเป็น basis point (1 bp = 0.01%) เพื่อคำนวณด้วยจำนวนเต็มล้วน
RATE_BP = {
    "silver": 150,    # 1.5%
    "gold": 250,      # 2.5%
    "platinum": 400,  # 4%
}

MIN_AMOUNT = 10_000    # 100 บาท (หน่วยสตางค์)
MAX_CASHBACK = 20_000  # 200 บาทต่อบิล (หน่วยสตางค์)
BIRTHDAY_MULTIPLIER = 2


def cashback(amount: int, tier: str, birthday: bool) -> int:
    """คืนจำนวนเงินคืนของบิลหนึ่งใบ เป็นจำนวนเต็มสตางค์.

    amount   ยอดซื้อ หน่วยสตางค์ (>= 0)
    tier     "silver" | "gold" | "platinum"
    birthday True ถ้าซื้อในเดือนเกิด (ได้เงินคืน 2 เท่า)
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    key = str(tier).strip().lower()
    if key not in RATE_BP:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r}")

    if amount < MIN_AMOUNT:
        return 0

    value = amount * RATE_BP[key] // 10_000  # ปัดเศษทิ้ง (floor) เป็นสตางค์
    if birthday:
        value *= BIRTHDAY_MULTIPLIER
    return min(value, MAX_CASHBACK)


if __name__ == "__main__":
    assert cashback(10_000, "silver", False) == 150       # 100 บาท 1.5% = 1.50 บาท
    assert cashback(9_999, "platinum", True) == 0         # ต่ำกว่า 100 บาท
    assert cashback(10_001, "silver", False) == 150       # ปัดเศษทิ้ง
    assert cashback(50_000, "gold", True) == 2_500        # 500 บาท 2.5% x2 = 25 บาท
    assert cashback(100_000, "platinum", False) == 4_000  # 1000 บาท 4% = 40 บาท
    assert cashback(1_000_000, "platinum", True) == 20_000  # 10,000 บาท 4% x2 = 800 บาท โดนเพดาน 200 บาท
    assert cashback(10_000_000, "gold", False) == 20_000  # 100,000 บาท 2.5% = 2500 บาท โดนเพดาน 200 บาท
    assert cashback(0, "gold", True) == 0
    assert cashback(50_000, " GOLD ", False) == 1_250     # tier ไม่สนตัวพิมพ์
    print("ok")
