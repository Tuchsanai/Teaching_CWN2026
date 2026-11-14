# หน่วย: สตางค์ (int) | ยอดหาร = total + total*tip/100 ปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียว
# หารเท่า ๆ กัน เศษแจกคนแรก ๆ คนละ 1 สตางค์


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def split_bill(total, people, tip_percent):
    if not _is_int(total) or total < 0:
        raise ValueError("total must be int >= 0")
    if not _is_int(people) or people < 1:
        raise ValueError("people must be int >= 1")
    if not _is_int(tip_percent) or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be int 0-100")
    num = total * (100 + tip_percent)
    grand = (2 * num + 100) // 200
    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]
