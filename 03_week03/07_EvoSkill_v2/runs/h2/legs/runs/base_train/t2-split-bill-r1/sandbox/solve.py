"""BaanKafe bill splitter."""


def split_bill(total, people, tip_percent):
    """Split a bill (in satang) among people, including a tip.

    total       -- bill amount in satang (>= 0)
    people      -- number of people (>= 1)
    tip_percent -- tip as an integer percentage (0-100)

    Returns a list of integer satang amounts, one per person, in order.
    The tip is rounded half-up to the nearest satang. Any remainder from
    dividing evenly is given, one satang each, to the first people in the list.
    """
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be between 0 and 100")

    # Integer arithmetic only: tip = total * tip_percent / 100, rounded half-up.
    tip = (total * tip_percent * 2 + 100) // 200
    grand_total = total + tip

    base, remainder = divmod(grand_total, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # 11000 / 3 -> [3667, 3667, 3666]
    print(split_bill(0, 4, 0))       # [0, 0, 0, 0]
    print(split_bill(999, 1, 15))    # [1149]
