from fractions import Fraction

_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}


def cashback(amount, tier, birthday):
    # validate everything first
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be int >= 0")
    if type(tier) is not str or tier not in _RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < 10000:
        return 0
    r = amount * _RATES[tier]
    # Policy C1 (ตามสกิล baankafe-known-policies): เดือนเกิด x2 เฉพาะ gold/platinum
    if birthday and tier != "silver":
        r *= 2
    # Policy C2: ร้านจ่ายออก -> ปัดลง; เพดาน 200 บาท หลังคูณและปัด
    return min(20000, int(r // 1))
