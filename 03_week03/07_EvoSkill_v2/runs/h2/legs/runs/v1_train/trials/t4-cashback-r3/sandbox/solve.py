"""BaanKafe: คิดเงินคืนสมาชิก

หน่วย: amount เป็นสตางค์ (จำนวนเต็ม >= 0), ผลลัพธ์เป็นสตางค์ (จำนวนเต็ม)
"""
import math
from fractions import Fraction

MIN_AMOUNT = 100 * 100        # ยอดขั้นต่ำ 100 บาท (สตางค์)
MAX_CASHBACK = 200 * 100      # เพดานเงินคืนต่อบิล 200 บาท (สตางค์)
RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(40, 1000),  # 4%
}


def _need_int(value, name, low=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    return value


def _need_bool(value, name):
    """flag: ต้องเป็น True หรือ False จริง"""
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def _need_choice(value, name, choices):
    """string ที่ต้องตรงตัวเลือกเป๊ะ (ไม่ strip, ไม่ lower)"""
    if type(value) is not str or value not in choices:
        raise ValueError(f"{name} ต้องเป็นหนึ่งใน {sorted(choices)}")
    return value


def cashback(amount, tier, birthday):
    """คืนค่าเงินคืนเป็นสตางค์ (จำนวนเต็ม)

    ลำดับการคิด:
      1. ยอด < 100 บาท -> 0
      2. amount * อัตราของ tier (ยังไม่ปัด)
      3. ซื้อในเดือนเกิด (birthday=True) -> คูณ 2
      4. จำกัดไม่เกิน 200 บาท
      5. ปัดลงเป็นจำนวนเต็มสตางค์ครั้งเดียว (เป็นเงินที่ร้านคืนให้ลูกค้า)
    """
    _need_int(amount, "amount", low=0)
    _need_choice(tier, "tier", set(RATES))
    _need_bool(birthday, "birthday")

    if amount < MIN_AMOUNT:
        return 0

    value = Fraction(amount) * RATES[tier]
    if birthday:
        value *= 2
    value = min(value, Fraction(MAX_CASHBACK))
    return math.floor(value)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน (หน่วยเป็นสตางค์)
    print(cashback(10000, "silver", False))   # 150  (100 บาท * 1.5%)
    print(cashback(10000, "gold", True))      # 500  (100 บาท * 2.5% * 2)
    print(cashback(500000, "platinum", False))  # 20000 (5,000 บาท * 4% = 200 บาท, พอดีเพดาน)
    print(cashback(9999, "platinum", True))   # 0    (ต่ำกว่า 100 บาท)
