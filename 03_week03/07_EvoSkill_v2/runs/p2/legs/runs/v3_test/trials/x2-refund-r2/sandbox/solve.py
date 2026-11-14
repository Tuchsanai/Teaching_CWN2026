# กติกา: paid = สตางค์ (int >= 0), used_percent = int 0-100, restock = bool
# ลำดับ: ใช้เกิน 80% (> 80) -> 0 ; คืนตามสัดส่วนที่เหลือ (100-used)/100 ;
# restock -> หักค่าดำเนินการ 12.5% ของยอดคืน (คูณ 7/8)
# ปัดเศษ: นโยบายข้อ 3 (เงินคืนที่ร้านจ่ายลูกค้า) -> floor ครั้งเดียวหลังคูณทุกอัตรา
from fractions import Fraction


class InvalidInput(ValueError, TypeError, KeyError):
    def __str__(self):
        return Exception.__str__(self)


def refund(paid, used_percent, restock):
    if type(paid) is not int or paid < 0:
        raise InvalidInput("paid must be int >= 0")
    if type(used_percent) is not int or not 0 <= used_percent <= 100:
        raise InvalidInput("used_percent must be int 0-100")
    if type(restock) is not bool:
        raise InvalidInput("restock must be bool")
    if used_percent > 80:
        return 0
    amount = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amount *= Fraction(7, 8)
    return int(amount.numerator // amount.denominator)
