from fractions import Fraction
import math

# หน่วยทั้งหมดเป็นสตางค์ (1 บาท = 100 สตางค์)
MIN_PURCHASE = 100 * 100      # ยอดซื้อขั้นต่ำ 100 บาท (ต่ำกว่านี้ไม่ได้เงินคืน)
MAX_CASHBACK = 200 * 100      # เงินคืนสูงสุดต่อบิล 200 บาท

# อัตราเงินคืน (เปอร์เซ็นต์)
RATES = {
    "silver": 1.5,
    "gold": 2.5,
    "platinum": 4,
}


def cashback(amount, tier, birthday):
    """คำนวณเงินคืนสมาชิก BaanKafe เป็นจำนวนเต็มสตางค์

    amount   : ยอดซื้อ หน่วยสตางค์ (จำนวนเต็ม >= 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด (ได้เงินคืน 2 เท่า)

    ลำดับการคิด:
      1. ยอดต่ำกว่า 100 บาท -> 0
      2. เงินคืนดิบ = ยอด × อัตรา% (เก็บเป็น Fraction ยังไม่ปัด)
      3. เดือนเกิด -> คูณ 2
      4. ปัดลงเป็นจำนวนเต็มสตางค์ (ปัดครั้งเดียวที่ขั้นสุดท้าย)
      5. ตัดเพดานที่ 200 บาท (ตัดหลังคูณ 2 แล้ว)
    """
    if not isinstance(amount, int) or isinstance(amount, bool):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    key = tier.strip().lower() if isinstance(tier, str) else tier
    if key not in RATES:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r} (ต้องเป็น silver, gold หรือ platinum)")

    if amount < MIN_PURCHASE:
        return 0

    raw = Fraction(amount) * Fraction(RATES[key]) / 100
    if birthday:
        raw *= 2
    value = math.floor(raw)
    return min(value, MAX_CASHBACK)


if __name__ == "__main__":
    # ตัวอย่างและกรณีขอบ (หน่วยสตางค์)
    checks = [
        (9999, "platinum", False, 0),        # ต่ำกว่า 100 บาท
        (10000, "silver", False, 150),       # พอดี 100 บาท: 1.5% = 1.50 บาท
        (10000, "silver", True, 300),        # เดือนเกิด 2 เท่า
        (100000, "gold", False, 2500),       # 1,000 บาท × 2.5%
        (100000, "platinum", True, 8000),    # 1,000 บาท × 4% × 2
        (500000, "platinum", False, 20000),  # 4% = 200 บาท พอดีเพดาน
        (500000, "gold", True, 20000),       # 2.5% × 2 = 250 บาท -> ตัดเพดาน 200
        (1000000, "silver", False, 15000),   # 1.5% = 150 บาท
        (33333, "silver", False, 499),       # 333.33 บาท × 1.5% = 4.99995 บาท -> ปัดลง 499 สตางค์
    ]
    for amount, tier, bday, expected in checks:
        got = cashback(amount, tier, bday)
        assert got == expected, (amount, tier, bday, got, expected)
    print("ตัวอย่างและกรณีขอบผ่านทั้งหมด")
