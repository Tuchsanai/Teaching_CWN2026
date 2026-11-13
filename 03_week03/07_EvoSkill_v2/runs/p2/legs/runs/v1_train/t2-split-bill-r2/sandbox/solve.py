# นโยบายปัดเศษ r2: ปัดครึ่งขึ้นเป็นสตางค์เต็มหลังคิดทิป แล้วค่อยหาร


def _check_int(name, v):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be an int")


def split_bill(total, people, tip_percent):
    _check_int("total", total)
    _check_int("people", people)
    _check_int("tip_percent", tip_percent)
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be in 0..100")

    tip = (total * tip_percent * 2 + 100) // 200  # half-up
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
