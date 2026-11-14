"""BaanKafe bill splitter."""


def split_bill(total, people, tip_percent):
    """Split a bill (in satang) among people, including tip.

    total       -- bill amount in satang (>= 0)
    people      -- number of people (>= 1)
    tip_percent -- tip as an integer percentage (0-100)

    Returns a list of integer satang amounts, one per person, in order.
    The tip is rounded half-up to the nearest satang. Any remainder from
    the division is paid one satang each by the first people in the list.
    """
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be between 0 and 100")

    tip = (total * tip_percent + 50) // 100
    amount = total + tip

    base, remainder = divmod(amount, people)
    return [base + 1] * remainder + [base] * (people - remainder)


if __name__ == "__main__":
    assert split_bill(10000, 3, 0) == [3334, 3333, 3333]
    assert split_bill(10000, 4, 10) == [2750, 2750, 2750, 2750]
    assert split_bill(0, 5, 50) == [0, 0, 0, 0, 0]
    assert split_bill(12345, 1, 15) == [14197]
    assert sum(split_bill(99999, 7, 33)) == 99999 + (99999 * 33 + 50) // 100
    print("all checks passed")
