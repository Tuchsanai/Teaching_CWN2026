# late_fee: หน่วยสตางค์ (int) ทั้งอินพุตและเอาต์พุต
# - days_late <= 3 -> 0 ; > 3 -> 0.75% (3/400) ของยอด ต่อวัน นับทุกวัน (รวม 3 วันแรก)
# - เพดาน 15% ของยอด ; ปัดเศษแบบข้อ 5 (half-up ครั้งเดียวตอนท้าย) ด้วยจำนวนเต็มล้วน
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
    # fee = amount * 75 * days / 10000 ; cap = amount * 15 / 100 = amount*1500/10000
    num = amount * min(75 * days_late, 1500)
    den = 10000
    return (2 * num + den) // (2 * den)
