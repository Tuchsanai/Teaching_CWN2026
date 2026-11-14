def split_bill(total, people, tip_percent):
    """Split a bill (in satang) plus tip among `people`.

    Tip is rounded half-up to a whole satang. Any remainder is distributed
    1 satang each to the first people.
    """
    if people < 1:
        raise ValueError("people must be >= 1")
    if total < 0:
        raise ValueError("total must be >= 0")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be between 0 and 100")

    tip = (total * tip_percent + 50) // 100
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
