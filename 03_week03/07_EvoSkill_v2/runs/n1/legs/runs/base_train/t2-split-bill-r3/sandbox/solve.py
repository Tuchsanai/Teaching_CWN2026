def split_bill(total, people, tip_percent):
    """Split a bill (in satang) among `people`, including a tip.

    The grand total is total + tip, with the tip rounded half up to a whole
    satang. Leftover satang go 1 each to the first people.
    """
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
