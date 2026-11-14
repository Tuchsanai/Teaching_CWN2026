from fractions import Fraction

# อัตราเงินคืนต่อ tier (เป็น Fraction เพื่อไม่ใช้ float)
RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(40, 1000),  # 4%
}

MIN_PURCHASE = 100 * 100   # 100 บาท ในหน่วยสตางค์
MAX_CASHBACK = 200 * 100   # 200 บาท ต่อบิล ในหน่วยสตางค์
BIRTHDAY_MULTIPLIER = 2


def _require_int(value, name):
    if type(value) is not int:  # ปฏิเสธ bool, float, str, None
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    return value


def _require_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def cashback(amount, tier, birthday):
    """คืนเงินคืนสมาชิก (จำนวนเต็มสตางค์)

    amount   : ยอดซื้อเป็นสตางค์ (int, >= 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด (ได้เงินคืน 2 เท่า)

    ผลลัพธ์ปัดลง (floor) เพราะเป็นเงินที่ร้านจ่ายให้ลูกค้า
    """
    _require_int(amount, "amount")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    if type(tier) is not str or tier not in RATES:  # ไม่ normalize
        raise ValueError(f"tier ต้องเป็นหนึ่งใน {sorted(RATES)}")

    _require_bool(birthday, "birthday")

    # ยอดต่ำกว่า 100 บาท ไม่ได้เงินคืน
    if amount < MIN_PURCHASE:
        return 0

    # คูณทุกตัวคูณก่อน แล้วค่อยปัดครั้งเดียว
    raw = Fraction(amount) * RATES[tier]
    if birthday:
        raw *= BIRTHDAY_MULTIPLIER

    cashback_amount = int(raw // 1)   # floor
    return min(cashback_amount, MAX_CASHBACK)


if __name__ == "__main__":
    print(cashback(10000, "silver", False))   # 150
    print(cashback(10000, "gold", True))      # 500
    print(cashback(1000000, "platinum", False))  # 20000 (ติดเพดาน)
