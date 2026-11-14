"""BaanKafe bill splitter.

split_bill(total, people, tip_percent) -> list[int]

- total: bill amount in satang (>= 0)
- people: number of people (>= 1)
- tip_percent: tip as an integer percentage (0-100)

The amount to split is total + tip. The tip is computed in whole satang
(rounded down). The amount is split evenly; any remainder satang is given
one each to the first people in order.
"""


def split_bill(total, people, tip_percent):
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise ValueError("total must be a non-negative integer (satang)")
    if not isinstance(people, int) or isinstance(people, bool) or people < 1:
        raise ValueError("people must be an integer >= 1")
    if not isinstance(tip_percent, int) or isinstance(tip_percent, bool) \
            or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be an integer between 0 and 100")

    tip = total * tip_percent // 100
    amount = total + tip

    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    # Quick examples
    print(split_bill(10000, 3, 0))    # [3334, 3333, 3333]
    print(split_bill(10000, 4, 10))   # [2750, 2750, 2750, 2750]
    print(split_bill(999, 2, 15))     # [574, 574]
