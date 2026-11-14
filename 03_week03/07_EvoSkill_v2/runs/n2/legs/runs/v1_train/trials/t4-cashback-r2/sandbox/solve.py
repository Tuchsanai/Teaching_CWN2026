from fractions import Fraction

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be int >= 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < 10000:  # ต่ำกว่า 100 บาท ไม่ได้เงินคืน
        return 0
    value = amount * RATES[tier]
    if birthday:
        value *= 2  # โจทย์ระบุ 2 เท่า ไม่แยกระดับ -> ใช้กับทุก tier รวม silver
    # เงินที่ร้านจ่ายออก -> ปัดทิ้ง (floor) แล้วจำกัดเพดาน 200 บาท
    return min(20000, int(value // 1))
