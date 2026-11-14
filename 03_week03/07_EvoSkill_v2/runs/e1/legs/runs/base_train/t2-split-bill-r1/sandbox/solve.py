def split_bill(total, people, tip_percent):
    """Split a bill (in satang) among `people`, including tip.

    The tip is total * tip_percent / 100, rounded down to whole satang.
    Any remainder is distributed 1 satang each to the first people.
    """
    if people < 1:
        raise ValueError("people must be >= 1")
    grand = total + total * tip_percent // 100
    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]
