# กติกา: paid/สตางค์ (int>=0), used_percent int 0-100, restock bool
# ลำดับ: คืนตามสัดส่วนที่ไม่ได้เรียน -> เรียนเกิน 80% (>80) = 0 -> หักค่าดำเนินการ 12.5% (ถ้า restock)
# ปัดเศษ: นโยบายข้อ 3 (เงินคืนที่ร้านจ่าย) -> floor ครั้งเดียวหลังคูณทุกอัตรา
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
    num, den = paid * (100 - used_percent), 100
    if restock:
        num, den = num * 7, den * 8  # x (1 - 12.5%)
    return num // den
