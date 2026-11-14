# split_bill rules
# - total: int satoshi-like units (สตางค์) >= 0; people: int >= 1; tip_percent: int 0..100
# - amount = total + tip, tip = total*tip_percent/100 rounded half-up once (to whole สตางค์)
# - split equally; remainder given +1 each to the first people
# - invalid input -> ValueError


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def split_bill(total, people, tip_percent):
    if not _is_int(total) or total < 0:
        raise ValueError("total must be an int >= 0")
    if not _is_int(people) or people < 1:
        raise ValueError("people must be an int >= 1")
    if not _is_int(tip_percent) or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be an int in 0..100")
    # tip = total*tip_percent/100, half-up
    tip = (2 * total * tip_percent + 100) // 200
    amount = total + tip
    base, rem = divmod(amount, people)
    return [base + 1 if i < rem else base for i in range(people)]
