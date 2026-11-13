def split_bill(total, people, tip_percent):
    """Split a bill (in satang) plus tip among `people`.

    The first `remainder` people each pay 1 satang extra.
    The total with tip is rounded half up to a whole satang.
    """
    grand = (total * (100 + tip_percent) * 2 + 100) // 200  # round half up
    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]
