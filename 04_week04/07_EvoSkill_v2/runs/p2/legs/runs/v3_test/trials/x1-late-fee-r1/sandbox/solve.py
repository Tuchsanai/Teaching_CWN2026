# late_fee: หน่วยสตางค์ (int) -> สตางค์ (int)
# กติกา: days_late <= 3 -> 0 ; มิฉะนั้น days_late * 0.75% ของ amount (นับทุกวัน) สูงสุด 15%
# ปัดเศษ: ข้อ 5 (สูตรเดียว) -> Fraction ตรง แล้วปัด half-up ครั้งเดียวตอนท้าย
from fractions import Fraction


class InvalidInput(ValueError, TypeError, KeyError):
    def __str__(self):
        return Exception.__str__(self)


def late_fee(amount, days_late):
    if type(amount) is not int or amount < 0:
        raise InvalidInput("amount must be int >= 0")
    if type(days_late) is not int or not 0 <= days_late <= 365:
        raise InvalidInput("days_late must be int in 0..365")
    if days_late <= 3:
        return 0
    rate = min(Fraction(75, 10000) * days_late, Fraction(15, 100))
    fee = rate * amount
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)
