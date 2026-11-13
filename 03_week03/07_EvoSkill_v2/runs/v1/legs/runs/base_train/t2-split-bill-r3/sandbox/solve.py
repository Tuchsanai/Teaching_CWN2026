def split_bill(total, people, tip_percent):
    """Split a bill (in satang) plus tip among `people`.

    Returns a list of integer satang amounts; the first people pay
    1 satang extra each when the amount doesn't divide evenly.
    """
    # Integer math only (no float error); round half up to whole satang.
    grand = (total * (100 + tip_percent) + 50) // 100
    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]
