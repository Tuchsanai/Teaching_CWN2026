"""BaanKafe: คำนวณเงินคืนสมาชิก (cashback)

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม)
- amount   : ยอดซื้อ (สตางค์, >= 0)
- tier     : "silver" | "gold" | "platinum" (ตัวพิมพ์เล็กเป๊ะ)
- birthday : True ถ้าซื้อในเดือนเกิด (ได้เงินคืน 2 เท่า)

กติกา
1. ยอดซื้อต่ำกว่า 100 บาท (10000 สตางค์) ไม่ได้เงินคืน
2. อัตรา: silver 1.5%, gold 2.5%, platinum 4%
3. เดือนเกิด ได้เงินคืน 2 เท่า
4. เงินคืนสูงสุด 200 บาท (20000 สตางค์) ต่อบิล
5. ผลลัพธ์เป็นจำนวนเต็มสตางค์

ลำดับการคำนวณ: ตรวจ input ทั้งหมด -> เกณฑ์ขั้นต่ำ -> คูณอัตรา -> คูณ 2 (เดือนเกิด)
-> เพดาน 200 บาท -> ปัดลงครั้งเดียว (เงินที่ร้านจ่ายออกให้ลูกค้า)
"""

from fractions import Fraction

MIN_AMOUNT = 10000        # 100 บาท
MAX_CASHBACK = 20000      # 200 บาท
BIRTHDAY_MULTIPLIER = 2
RATES = {
    "silver": Fraction(15, 1000),   # 1.5%
    "gold": Fraction(25, 1000),     # 2.5%
    "platinum": Fraction(4, 100),   # 4%
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
    """ค่า string ที่ต้องตรงตัวเลือกเป๊ะ (ไม่ strip, ไม่ lower)"""
    if type(value) is not str or value not in choices:
        raise ValueError(f"{name} ต้องเป็นหนึ่งใน {sorted(choices)}")
    return value


def cashback(amount, tier, birthday):
    """คืนจำนวนเงินคืนเป็นสตางค์ (จำนวนเต็ม)"""
    # 1) ตรวจ input ทุกตัวก่อนเข้าเงื่อนไขธุรกิจ
    _need_int(amount, "amount", low=0)
    _need_choice(tier, "tier", RATES)
    _need_bool(birthday, "birthday")

    # 2) เกณฑ์ขั้นต่ำ (ต่ำกว่า 100 บาท ไม่ได้เงินคืน)
    if amount < MIN_AMOUNT:
        return 0

    # 3) คำนวณแบบ exact โดยยังไม่ปัด
    value = amount * RATES[tier]
    if birthday:
        value *= BIRTHDAY_MULTIPLIER

    # 4) เพดานต่อบิล
    value = min(value, MAX_CASHBACK)

    # 5) ปัดลงครั้งเดียวตอนท้าย (ร้านไม่จ่ายเกินให้ลูกค้า)
    return int(value // 1)


if __name__ == "__main__":
    print(cashback(10000, "gold", True))   # 500
    print(cashback(40060, "gold", False))  # 1001
