"""BaanKafe cashback calculator.

ยอดซื้อ (amount) และเงินคืน ใช้หน่วย "สตางค์" (1 บาท = 100 สตางค์) เป็นจำนวนเต็มทั้งหมด
เพื่อหลีกเลี่ยงปัญหาทศนิยมของ float
"""

# อัตราเงินคืนต่อระดับสมาชิก เก็บเป็นส่วนในพัน (permille) เพื่อใช้จำนวนเต็ม
# silver 1.5% = 15/1000, gold 2.5% = 25/1000, platinum 4% = 40/1000
RATE_PERMILLE = {
    "silver": 15,
    "gold": 25,
    "platinum": 40,
}

MIN_PURCHASE = 100 * 100      # ยอดซื้อขั้นต่ำ 100 บาท = 10,000 สตางค์
MAX_CASHBACK = 200 * 100      # เงินคืนสูงสุดต่อบิล 200 บาท = 20,000 สตางค์
BIRTHDAY_MULTIPLIER = 2       # เดือนเกิด ได้เงินคืน 2 เท่า


def cashback(amount, tier, birthday=False):
    """คำนวณเงินคืนสมาชิก (หน่วยสตางค์, จำนวนเต็ม)

    amount   : ยอดซื้อ หน่วยสตางค์ (int, >= 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด

    กติกา:
      1. ยอดซื้อต่ำกว่า 100 บาท -> ไม่ได้เงินคืน (0)
      2. เงินคืน = ยอดซื้อ * อัตราของระดับสมาชิก (ปัดทิ้งเศษเป็นสตางค์จำนวนเต็ม)
      3. เดือนเกิด -> คูณ 2
      4. จำกัดไม่เกิน 200 บาทต่อบิล
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    key = tier.strip().lower() if isinstance(tier, str) else tier
    if key not in RATE_PERMILLE:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r} (ต้องเป็น silver, gold หรือ platinum)")

    if amount < MIN_PURCHASE:
        return 0

    result = amount * RATE_PERMILLE[key] // 1000

    if birthday:
        result *= BIRTHDAY_MULTIPLIER

    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน (หน่วยสตางค์)
    print(cashback(5000, "gold"))                 # 0   ต่ำกว่า 100 บาท
    print(cashback(10000, "silver"))              # 150 = 1.50 บาท
    print(cashback(10000, "silver", True))        # 300 = 3.00 บาท
    print(cashback(1000000, "platinum"))          # 20000 = 200 บาท (ถึงเพดาน)
    print(cashback(1000000, "platinum", True))    # 20000 = 200 บาท (ถึงเพดาน)
    print(cashback(333, "gold"))                  # 0   ต่ำกว่า 100 บาท
    print(cashback(10001, "gold"))                # 250 = 2.50 บาท (ปัดทิ้งเศษ)
