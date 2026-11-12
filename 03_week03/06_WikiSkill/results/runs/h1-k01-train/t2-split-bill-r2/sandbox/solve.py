"""BaanKafe bill splitter.

All money is handled as integer satang to avoid floating-point error.
"""


def split_bill(total, people, tip_percent):
    """Split a bill (plus tip) evenly among people.

    Args:
        total: bill amount in satang (>= 0).
        people: number of people (>= 1).
        tip_percent: tip as an integer percentage (0-100).

    Returns:
        list[int]: amount each person pays in satang, in person order.
        Any remainder satang is given one each to the first people.
    """
    if not isinstance(total, int) or total < 0:
        raise ValueError("total must be a non-negative integer (satang)")
    if not isinstance(people, int) or people < 1:
        raise ValueError("people must be an integer >= 1")
    if not isinstance(tip_percent, int) or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be an integer between 0 and 100")

    # Tip in satang, rounded half up to the nearest satang (integer math only).
    tip = (total * tip_percent * 2 + 100) // 200
    amount = total + tip

    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # 11000 satang over 3 -> [3667, 3667, 3666]
