def _check_int(name, v):
    if isinstance(v, bool):
        raise TypeError(f"{name} must be int, not bool")
    if isinstance(v, float):
        if not v.is_integer():
            raise ValueError(f"{name} must be an integer")
        return int(v)
    if not isinstance(v, int):
        raise TypeError(f"{name} must be int")
    return int(v)


def split_bill(total, people, tip_percent):
    total = _check_int("total", total)
    people = _check_int("people", people)
    tip_percent = _check_int("tip_percent", tip_percent)
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be in 0..100")
    # tip rounded half up, once, to whole satang
    tip = (2 * total * tip_percent + 100) // 200
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
