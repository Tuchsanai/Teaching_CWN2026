"""BaanKafe bill splitter."""


def split_bill(total, people, tip_percent):
    """Split a bill (in satang) among people, including tip.

    total       -- bill amount in satang (>= 0)
    people      -- number of people (>= 1)
    tip_percent -- tip as an integer percentage (0-100)

    Returns a list of integer satang amounts, one per person, in order.
    The tip is rounded half-up to the nearest satang. Any leftover satang
    from uneven division are given one each to the first persons in the list.
    """
    if not isinstance(total, int) or not isinstance(people, int) or not isinstance(tip_percent, int):
        raise TypeError("total, people and tip_percent must be integers")
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be between 0 and 100")

    # Integer-only rounding half-up of total * tip_percent / 100.
    tip = (total * tip_percent * 2 + 100) // 200
    amount = total + tip

    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # 11000 / 3 -> [3667, 3667, 3666]
    print(split_bill(0, 4, 0))       # [0, 0, 0, 0]
    print(split_bill(999, 2, 15))    # 1148.85 -> tip 150 -> 1149 -> [575, 574]
