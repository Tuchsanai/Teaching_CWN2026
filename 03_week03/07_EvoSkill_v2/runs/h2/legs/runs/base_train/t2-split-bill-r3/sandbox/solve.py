"""BaanKafe bill splitter.

split_bill(total, people, tip_percent) -> list[int]

- total: bill amount in satang (integer >= 0)
- people: number of people (integer >= 1)
- tip_percent: tip as a whole-number percentage (integer 0-100)

The amount to split is total + tip, where tip = total * tip_percent / 100
(rounded down to the nearest satang, so all values stay integers).
The amount is split evenly; any remainder satang is given one each to the
first people in order. Returns each person's payment in satang, in order.
"""


def split_bill(total: int, people: int, tip_percent: int) -> list[int]:
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
    assert split_bill(10000, 4, 10) == [2750, 2750, 2750, 2750]
    assert split_bill(0, 2, 50) == [0, 0]
    assert split_bill(999, 1, 0) == [999]
    assert sum(split_bill(12345, 7, 15)) == 12345 + 12345 * 15 // 100
    print("all checks passed")
