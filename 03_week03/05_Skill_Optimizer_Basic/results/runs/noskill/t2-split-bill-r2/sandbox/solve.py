def split_bill(total, people, tip_percent):
    """Split a bill (in satang) among `people`, including tip.

    Tip is rounded half-up to a whole satang. Any remainder is distributed
    one satang each to the first people.
    """
    if total < 0 or people < 1 or not 0 <= tip_percent <= 100:
        raise ValueError("invalid arguments")
    tip = (total * tip_percent * 2 + 100) // 200  # round half up, integer math
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
