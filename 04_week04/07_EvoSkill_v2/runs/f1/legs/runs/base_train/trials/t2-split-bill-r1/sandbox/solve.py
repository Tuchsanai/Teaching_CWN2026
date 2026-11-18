def split_bill(total, people, tip_percent):
    """Split a bill (in satang) plus tip among `people`; first people pay the extra satang."""
    if people < 1:
        raise ValueError("people must be >= 1")
    if total < 0:
        raise ValueError("total must be >= 0")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be in 0..100")

    # Integer arithmetic (no float error); round half up to whole satang.
    grand = (total * (100 + tip_percent) * 2 + 100) // 200
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
