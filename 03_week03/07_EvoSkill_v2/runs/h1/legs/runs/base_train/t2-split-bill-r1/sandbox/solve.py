"""BaanKafe bill splitter.

split_bill(total, people, tip_percent) -> list[int]

- total: bill amount in satang (>= 0)
- people: number of people (>= 1)
- tip_percent: tip as an integer percentage (0-100)

The amount to split is total + tip. The tip is computed in integer satang
(rounded down), so every amount stays an integer. The amount is split evenly;
if it does not divide evenly, the first people in the list each pay one extra
satang until the remainder is used up.
"""


def split_bill(total, people, tip_percent):
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise ValueError("total must be a non-negative integer (satang)")
    if not isinstance(people, int) or isinstance(people, bool) or people < 1:
        raise ValueError("people must be an integer >= 1")
    if not isinstance(tip_percent, int) or isinstance(tip_percent, bool) or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be an integer between 0 and 100")

    tip = total * tip_percent // 100
    amount = total + tip

    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    assert split_bill(10000, 3, 0) == [3334, 3333, 3333]
    assert sum(split_bill(10000, 3, 0)) == 10000
    assert split_bill(10000, 4, 10) == [2750, 2750, 2750, 2750]
    assert split_bill(0, 2, 50) == [0, 0]
    assert split_bill(1, 3, 0) == [1, 0, 0]
    assert split_bill(999, 1, 100) == [1998]
    result = split_bill(12345, 5, 7)
    assert sum(result) == 12345 + 12345 * 7 // 100
    assert max(result) - min(result) <= 1
    assert result == sorted(result, reverse=True)
    print("all checks passed")
