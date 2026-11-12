"""BaanKafe bill splitter.

All money values are integers in satang (1 baht = 100 satang).
"""


def split_bill(total: int, people: int, tip_percent: int) -> list[int]:
    """Split a bill (plus tip) evenly among `people`.

    Args:
        total: bill amount in satang, >= 0.
        people: number of people, >= 1.
        tip_percent: tip as an integer percentage, 0-100.

    Returns:
        List of amounts (satang) each person pays, in person order.
        The first `remainder` people pay one extra satang so the total is exact.

    Tip is computed with integer math and rounded down to the whole satang.
    """
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be between 0 and 100")

    tip = total * tip_percent // 100
    amount = total + tip

    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    # Quick examples
    print(split_bill(10000, 3, 10))  # 11000 / 3 -> [3667, 3667, 3666]
    print(split_bill(0, 4, 0))       # [0, 0, 0, 0]
    print(split_bill(999, 1, 100))   # [1998]
