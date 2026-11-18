def split_bill(total, people, tip_percent):
    """Split a bill (in satang) plus tip among `people`.

    The grand total is rounded half-up to a whole satang. Any remainder is
    distributed 1 satang each to the first people.
    """
    if people < 1:
        raise ValueError("people must be >= 1")
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
