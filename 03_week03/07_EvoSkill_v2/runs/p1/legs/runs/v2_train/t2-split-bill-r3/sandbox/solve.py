def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def split_bill(total, people, tip_percent):
    if not (_is_int(total) and _is_int(people) and _is_int(tip_percent)):
        raise ValueError("total, people, tip_percent must be int")
    if total < 0 or people < 1 or not (0 <= tip_percent <= 100):
        raise ValueError("input out of range")
    # tip = floor(total * tip / 100), integer arithmetic, floor once
    grand = total + (total * tip_percent) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
