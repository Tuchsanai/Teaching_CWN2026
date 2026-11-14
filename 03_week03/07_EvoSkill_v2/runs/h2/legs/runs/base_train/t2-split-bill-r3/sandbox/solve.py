"""BaanKafe bill splitter.

All money is handled as integer satang (1 baht = 100 satang) to avoid
floating-point error.
"""


def split_bill(total: int, people: int, tip_percent: int) -> list[int]:
    """Split a bill (plus tip) evenly among `people`.

    Args:
        total: bill amount in satang (>= 0).
        people: number of people sharing the bill (>= 1).
        tip_percent: tip as an integer percentage (0-100).

    Returns:
        A list of length `people` with the amount in satang each person pays,
        in person order. The first few people pay 1 satang more when the
        amount does not divide evenly, so the list always sums to the total
        plus tip.
    """
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be between 0 and 100")

    # Tip in satang, rounded half-up using integer arithmetic only.
    tip = (total * tip_percent * 2 + 100) // 200
    amount = total + tip

    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # 100 baht, 10% tip, 3 people
    print(split_bill(0, 4, 0))       # [0, 0, 0, 0]
    print(split_bill(1, 3, 0))       # [1, 0, 0]
