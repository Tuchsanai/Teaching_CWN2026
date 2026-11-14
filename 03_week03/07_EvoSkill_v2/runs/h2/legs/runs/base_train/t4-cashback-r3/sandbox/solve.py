"""BaanKafe member cashback calculator.

Amounts are in satang (1 baht = 100 satang). All arithmetic is integer-only,
so the result is always a whole number of satang.
"""

# อัตราเงินคืนต่อระดับสมาชิก เก็บเป็นส่วนในพัน (permille) เพื่อหลีกเลี่ยงทศนิยม
# silver 1.5% = 15/1000, gold 2.5% = 25/1000, platinum 4% = 40/1000
RATE_PERMILLE = {
    "silver": 15,
    "gold": 25,
    "platinum": 40,
}

MIN_AMOUNT = 100 * 100        # ยอดซื้อขั้นต่ำ 100 บาท (satang)
MAX_CASHBACK = 200 * 100      # เงินคืนสูงสุดต่อบิล 200 บาท (satang)
BIRTHDAY_MULTIPLIER = 2       # เดือนเกิดได้เงินคืน 2 เท่า


def cashback(amount, tier, birthday=False):
    """Return the cashback in satang for one bill.

    amount   -- purchase total in satang (int, >= 0)
    tier     -- "silver", "gold" or "platinum"
    birthday -- True if the purchase is in the member's birthday month

    Rules:
      * amount < 100 baht          -> 0
      * rate by tier               -> silver 1.5%, gold 2.5%, platinum 4%
      * birthday month             -> cashback doubled
      * cap at 200 baht per bill
      * result is floored to whole satang
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount must be an int (satang)")
    if amount < 0:
        raise ValueError("amount must be >= 0")

    key = tier.strip().lower() if isinstance(tier, str) else tier
    if key not in RATE_PERMILLE:
        raise ValueError(f"unknown tier: {tier!r}")

    if amount < MIN_AMOUNT:
        return 0

    multiplier = BIRTHDAY_MULTIPLIER if birthday else 1
    result = amount * RATE_PERMILLE[key] * multiplier // 1000
    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    # ตัวอย่างและการทดสอบพื้นฐาน
    assert cashback(9999, "gold") == 0                 # ต่ำกว่า 100 บาท
    assert cashback(10000, "silver") == 150            # 100 บาท * 1.5% = 1.50 บาท
    assert cashback(10000, "silver", True) == 300      # เดือนเกิด x2
    assert cashback(50000, "gold") == 1250             # 500 บาท * 2.5% = 12.50 บาท
    assert cashback(1000000, "platinum") == 20000      # 4% = 400 บาท -> ติดเพดาน 200 บาท
    assert cashback(10000, "Platinum") == 400          # 100 บาท * 4% = 4 บาท
    assert cashback(7777, "silver") == 0               # ไม่ถึง 100 บาท
    print("all checks passed")
