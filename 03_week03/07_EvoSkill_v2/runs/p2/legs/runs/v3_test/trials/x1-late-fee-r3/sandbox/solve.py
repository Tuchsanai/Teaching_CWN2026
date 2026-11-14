# หน่วย: amount เป็นสตางค์ (int >= 0), days_late int 0-365, ผลลัพธ์เป็นสตางค์ int
# ลำดับ: days<=3 -> 0; ไม่เช่นนั้น fee = amount*0.75%*days (นับทุกวัน) -> cap 15% ของ amount
# ปัดเศษ: นโยบายข้อ 5 -> Fraction ตลอด แล้วปัด half-up ครั้งเดียวตอนท้าย
from fractions import Fraction


class InvalidInput(ValueError, TypeError, KeyError):
    def __str__(self):
        return Exception.__str__(self)


def late_fee(amount, days_late):
    if type(amount) is not int or amount < 0:
        raise InvalidInput("amount must be int >= 0")
    if type(days_late) is not int or not (0 <= days_late <= 365):
        raise InvalidInput("days_late must be int in 0..365")
    if days_late <= 3:
        return 0
    fee = Fraction(amount * 75 * days_late, 10000)
    cap = Fraction(amount * 15, 100)
    if fee > cap:
        fee = cap
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)
