"""คำนวณเงินคืนสมาชิกของร้าน BaanKafe

หน่วยทั้งหมดเป็นสตางค์ (integer) เพื่อหลีกเลี่ยงปัญหาความคลาดเคลื่อนของ float
อัตราเก็บเป็น basis points (1 bp = 0.01%) เช่น 1.5% = 150 bp
"""

MIN_PURCHASE = 10_000      # 100 บาท (สตางค์)
MAX_CASHBACK = 20_000      # 200 บาทต่อบิล (สตางค์)
BASIS = 10_000             # ตัวหาร basis points (100% = 10000 bp)

RATES_BP = {
    "silver": 150,         # 1.5%
    "gold": 250,           # 2.5%
    "platinum": 400,       # 4%
}


def cashback(amount: int, tier: str, birthday: bool) -> int:
    """คืนจำนวนเงินคืน (สตางค์, จำนวนเต็ม) สำหรับบิลหนึ่งใบ

    amount   : ยอดซื้อ หน่วยสตางค์ (จำนวนเต็ม >= 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด (ได้เงินคืน 2 เท่า)

    เงื่อนไข:
      - ยอดซื้อต่ำกว่า 100 บาท ไม่ได้เงินคืน
      - เงินคืน = ยอด * อัตราของระดับสมาชิก (ปัดลงเป็นจำนวนเต็มสตางค์)
      - เดือนเกิดได้ 2 เท่า
      - เงินคืนสูงสุด 200 บาทต่อบิล (ตัดหลังคูณ 2 เท่าแล้ว)

    raise ValueError ถ้า amount ติดลบ/ไม่ใช่จำนวนเต็ม หรือ tier ไม่รู้จัก
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if tier not in RATES_BP:
        raise ValueError(f"tier ไม่รู้จัก: {tier!r}")

    if amount < MIN_PURCHASE:
        return 0

    result = amount * RATES_BP[tier]
    if birthday:
        result *= 2
    result //= BASIS  # ปัดลงเป็นจำนวนเต็มสตางค์

    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    # ตัวอย่างการทดสอบอย่างรวดเร็ว
    cases = [
        (9_999, "platinum", False, 0),        # ต่ำกว่า 100 บาท
        (10_000, "silver", False, 150),       # 100 บาท * 1.5% = 1.50 บาท
        (10_000, "silver", True, 300),        # เดือนเกิด 2 เท่า
        (10_000, "gold", False, 250),         # 2.5%
        (10_000, "platinum", False, 400),     # 4%
        (50_000, "gold", True, 2_500),        # 500 บาท * 2.5% * 2 = 25 บาท
        (1_000_000, "platinum", False, 20_000),  # ถูกตัดที่ 200 บาท
        (1_000_000, "platinum", True, 20_000),   # ถูกตัดที่ 200 บาท
        (5_050, "silver", False, 0),          # ต่ำกว่า 100 บาท
        (12_345, "gold", False, 308),         # 123.45 * 2.5% = 3.08625 -> 308 สตางค์ (ปัดลง)
    ]
    for amount, tier, bday, expected in cases:
        got = cashback(amount, tier, bday)
        status = "OK " if got == expected else "FAIL"
        print(f"{status} cashback({amount}, {tier!r}, {bday}) = {got} (expected {expected})")
