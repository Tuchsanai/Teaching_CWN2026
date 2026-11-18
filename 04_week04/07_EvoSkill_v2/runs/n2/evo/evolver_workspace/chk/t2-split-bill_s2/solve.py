def _need_int(v, lo, hi=None):
    if type(v) is not int or v < lo or (hi is not None and v > hi):
        raise ValueError("invalid input")


def split_bill(total, people, tip_percent):
    _need_int(total, 0)
    _need_int(people, 1)
    _need_int(tip_percent, 0, 100)
    # grand total rounded half-up once (house rule); tip not rounded separately
    grand = (total * (100 + tip_percent) * 2 + 100) // 200
    base, extra = divmod(grand, people)
    return [base + 1] * extra + [base] * (people - extra)
