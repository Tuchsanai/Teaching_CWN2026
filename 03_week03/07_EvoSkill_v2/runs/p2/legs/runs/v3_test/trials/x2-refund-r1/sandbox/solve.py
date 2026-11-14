# refund(paid, used_percent, restock)
# หน่วย: paid สตางค์ (int >= 0), used_percent int 0-100, restock bool; คืนเป็น int สตางค์
# ลำดับ: used > 80 -> 0; ยอดคืน = paid*(100-used)/100; restock -> หัก 12.5% (คูณ 7/8)
# ปัดเศษ: นโยบายข้อ 3 (เงินคืน) -> floor ครั้งเดียวหลังคูณทุกอย่างแล้ว ด้วยจำนวนเต็มล้วน
class InvalidInput(ValueError, TypeError, KeyError):
    def __str__(self):
        return Exception.__str__(self)


def refund(paid, used_percent, restock):
    if type(paid) is not int or paid < 0:
        raise InvalidInput("paid must be int >= 0")
    if type(used_percent) is not int or not (0 <= used_percent <= 100):
        raise InvalidInput("used_percent must be int 0-100")
    if type(restock) is not bool:
        raise InvalidInput("restock must be bool")
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7
        den *= 8
    return int(num // den)
