# หน่วย: สตางค์ (int) · ยอดหาร = total + tip (ทิป = total*tip_percent/100 ปัดครึ่งขึ้น)
# หาร people คน: คนแรก ๆ ได้ +1 สตางค์ตามเศษ


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def split_bill(total, people, tip_percent):
    if not _is_int(total) or total < 0:
        raise ValueError("total must be int >= 0")
    if not _is_int(people) or people < 1:
        raise ValueError("people must be int >= 1")
    if not _is_int(tip_percent) or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be int in 0..100")
    grand = (2 * total * (100 + tip_percent) + 100) // 200
    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]
