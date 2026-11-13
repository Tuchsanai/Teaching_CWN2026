def split_bill(total, people, tip_percent):
    """Split a bill (in satang) among `people`, including tip.

    The grand total is total + tip, rounded half up to a whole satang.
    Any remainder is distributed 1 satang each to the first people.
    """
    if people < 1:
        raise ValueError("people must be >= 1")
    grand = (total * (100 + tip_percent) + 50) // 100  # integer math, no float error
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
