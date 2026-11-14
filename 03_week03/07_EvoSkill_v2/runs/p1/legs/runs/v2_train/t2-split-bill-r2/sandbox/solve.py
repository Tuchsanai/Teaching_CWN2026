def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def split_bill(total, people, tip_percent):
    if not (_is_int(total) and _is_int(people) and _is_int(tip_percent)):
        raise ValueError("total, people, tip_percent must be int")
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be in 0..100")

    # tip = floor(total * tip / 100), single floor at the end (integer math)
    grand = total + (total * tip_percent) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
