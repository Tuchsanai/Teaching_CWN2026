class InputError(ValueError, TypeError):
    pass


def _is_int(x):
    return type(x) is int


def split_bill(total, people, tip_percent):
    if not _is_int(total) or total < 0:
        raise InputError("total must be int >= 0")
    if not _is_int(people) or people < 1:
        raise InputError("people must be int >= 1")
    if not _is_int(tip_percent) or not 0 <= tip_percent <= 100:
        raise InputError("tip_percent must be int in 0..100")
    # tip rounded half up once, to whole satang
    tip = (2 * total * tip_percent + 100) // 200
    grand = total + tip
    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]
