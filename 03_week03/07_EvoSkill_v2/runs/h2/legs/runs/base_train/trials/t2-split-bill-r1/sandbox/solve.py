"""BaanKafe bill splitter.

split_bill(total, people, tip_percent) -> list[int]

- total        : bill amount in satang (>= 0)
- people       : number of people (>= 1)
- tip_percent  : tip as an integer percentage (0..100)

The amount to split is total + tip. The tip is rounded to the nearest satang
(half up) so that everything stays in integer arithmetic. The amount is split
evenly; any remainder satang is given one each to the first people in order.
"""


def split_bill(total: int, people: int, tip_percent: int) -> list[int]:
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise ValueError("total must be a non-negative integer (satang)")
    if not isinstance(people, int) or isinstance(people, bool) or people < 1:
        raise ValueError("people must be an integer >= 1")
    if not isinstance(tip_percent, int) or isinstance(tip_percent, bool) \
            or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be an integer in 0..100")

    # Tip in satang, rounded half up: floor((total * pct + 50) / 100)
    tip = (total * tip_percent + 50) // 100
    amount = total + tip

    base, remainder = divmod(amount, people)
    # First `remainder` people pay one extra satang each.
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    # Quick sanity checks
    assert split_bill(10000, 3, 0) == [3334, 3333, 3333]
    assert sum(split_bill(10000, 3, 0)) == 10000
    assert split_bill(10000, 4, 10) == [2750, 2750, 2750, 2750]  # 11000 / 4
    assert split_bill(0, 2, 50) == [0, 0]
    assert split_bill(1, 1, 0) == [1]
    assert split_bill(333, 2, 15) == [192, 191]  # 333 + 50 = 383 -> 192 + 191
    assert split_bill(12345, 5, 7) == [2642, 2642, 2642, 2642, 2641]  # tip 864 -> 13209
    print("all checks passed")
