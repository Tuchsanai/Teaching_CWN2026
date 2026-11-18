from fractions import Fraction

# อัตราเงินคืนตาม tier (หน่วย: เปอร์เซ็นต์)
RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(4, 100),    # 4%
}

MIN_PURCHASE = 10_000    # 100 บาท (สตางค์)
BIRTHDAY_MULTIPLIER = 2  # เดือนเกิดได้ 2 เท่า
MAX_CASHBACK = 20_000    # 200 บาท (สตางค์) ต่อบิล


def _require_int(value, name):
    # ปฏิเสธ bool, float, str, None (ห้ามแปลงค่าเงียบ ๆ)
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if value < 0:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า 0")
    return value


def _require_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def _require_tier(value):
    if type(value) is not str or value not in RATES:
        raise ValueError(f"tier ต้องเป็นหนึ่งใน {sorted(RATES)}")
    return value


def cashback(amount, tier, birthday):
    """คำนวณเงินคืนสมาชิกเป็นสตางค์ (จำนวนเต็ม)

    amount   : ยอดซื้อเป็นสตางค์ (int, >= 0)
    tier     : "silver", "gold" หรือ "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด
    """
    amount = _require_int(amount, "amount")
    tier = _require_tier(tier)
    birthday = _require_bool(birthday, "birthday")

    # ยอดต่ำกว่า 100 บาท ไม่ได้เงินคืน
    if amount < MIN_PURCHASE:
        return 0

    # คูณทุกตัวคูณก่อน แล้วค่อยปัดลง (ร้านจ่ายออกให้ลูกค้า จึงไม่จ่ายเกินสิทธิ์)
    raw = Fraction(amount) * RATES[tier]
    if birthday:
        raw *= BIRTHDAY_MULTIPLIER
    cb = int(raw // 1)

    # เพดานหลังคูณทั้งหมดแล้ว
    return min(cb, MAX_CASHBACK)


if __name__ == "__main__":
    print(cashback(10_000, "silver", False))   # 150
    print(cashback(100_000, "gold", True))     # 5000
    print(cashback(1_000_000, "platinum", False))  # 20000 (ถึงเพดาน)
