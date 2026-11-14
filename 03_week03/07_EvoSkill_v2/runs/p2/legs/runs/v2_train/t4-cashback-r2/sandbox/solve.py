from fractions import Fraction

# แบบ E: Fraction ตลอด ปัดครึ่งไปหาเลขคู่ (banker's) ครั้งเดียวตอนท้าย ไม่ตรวจอินพุต
_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}


def cashback(amount, tier, birthday):
    if amount < 10000:  # ต่ำกว่า 100 บาท ไม่ได้เงินคืน
        return 0
    v = Fraction(amount) * _RATES[tier]
    if birthday:
        v *= 2
    v = min(v, Fraction(20000))  # เพดาน 200 บาทต่อบิล (หลังคูณ 2)
    return int(round(v))
