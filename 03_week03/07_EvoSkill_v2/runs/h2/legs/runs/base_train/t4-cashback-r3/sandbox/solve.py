"""BaanKafe member cashback calculator.

Units: all amounts are in satang (1 บาท = 100 สตางค์), as integers.
"""

MIN_AMOUNT = 100 * 100          # ยอดซื้อขั้นต่ำ 100 บาท = 10000 สตางค์
MAX_CASHBACK = 200 * 100        # เงินคืนสูงสุดต่อบิล 200 บาท = 20000 สตางค์

# อัตราเงินคืนเป็นหน่วย basis points (1 bp = 0.01%) เพื่อให้คำนวณด้วยจำนวนเต็มล้วน
RATE_BP = {
    "silver": 150,     # 1.5%
    "gold": 250,       # 2.5%
    "platinum": 400,   # 4%
}


def cashback(amount: int, tier: str, birthday: bool = False) -> int:
    """คืนค่าเงินคืนเป็นสตางค์ (จำนวนเต็ม, ปัดทิ้งเศษสตางค์)

    amount   : ยอดซื้อ หน่วยสตางค์ (>= 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด (ได้เงินคืน 2 เท่า ก่อนคิดเพดาน)
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    key = tier.strip().lower() if isinstance(tier, str) else tier
    if key not in RATE_BP:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r} (ต้องเป็น silver, gold หรือ platinum)")

    if amount < MIN_AMOUNT:
        return 0

    result = amount * RATE_BP[key] // 10000
    if birthday:
        result *= 2

    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(cashback(10000, "silver"))                # 100 บาท -> 1.5 บาท = 150
    print(cashback(10000, "gold", birthday=True))   # 100 บาท *2.5% *2 = 5 บาท = 500
    print(cashback(1000000, "platinum"))            # 10,000 บาท *4% = 400 บาท -> เพดาน 200 บาท = 20000
    print(cashback(9999, "platinum"))               # ต่ำกว่า 100 บาท -> 0
