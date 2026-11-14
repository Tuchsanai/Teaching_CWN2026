"""BaanKafe bill splitter.

All money is handled as integer satang to avoid floating-point error.
"""


def split_bill(total, people, tip_percent):
    """Split a bill (in satang) evenly among people, including tip.

    Args:
        total: bill amount in satang (>= 0).
        people: number of people sharing the bill (>= 1).
        tip_percent: tip as an integer percentage (0-100).

    Returns:
        A list of integers (satang), one per person, in person order.
        The first few people pay an extra satang when the amount does not
        divide evenly.

    Raises:
        ValueError: if any argument is out of range.
    """
    if not isinstance(total, int) or total < 0:
        raise ValueError("total must be a non-negative integer (satang)")
    if not isinstance(people, int) or people < 1:
        raise ValueError("people must be an integer >= 1")
    if not isinstance(tip_percent, int) or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be an integer between 0 and 100")

    # Tip rounded half-up to the nearest satang, using integer arithmetic only.
    tip = (total * tip_percent + 50) // 100
    amount = total + tip

    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # 11000 satang -> [3667, 3667, 3666]
    print(split_bill(0, 4, 0))       # [0, 0, 0, 0]
    print(split_bill(12345, 1, 0))   # [12345]
