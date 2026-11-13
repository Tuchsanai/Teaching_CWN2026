from fractions import Fraction


def _need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def _half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def split_bill(total, people, tip_percent):
    _need_int(total, "total", 0)
    _need_int(people, "people", 1)
    _need_int(tip_percent, "tip_percent", 0, 100)
    grand = _half_up(Fraction(total) * (100 + tip_percent) / 100)
    base, extra = divmod(grand, people)
    return [base + 1] * extra + [base] * (people - extra)
