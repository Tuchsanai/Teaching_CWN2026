def split_bill(total, people, tip_percent):
    """Split a bill (in satang) among `people`, including tip.

    The tip is rounded half-up to a whole satang. Any remainder is
    distributed 1 satang each to the first people.
    """
    tip = (total * tip_percent * 2 + 100) // 200  # round half up
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
