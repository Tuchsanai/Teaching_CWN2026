"""BaanKafe bill splitter.

split_bill(total, people, tip_percent) -> list[int]

- total        : bill amount in satang (integer, >= 0)
- people       : number of people (integer, >= 1)
- tip_percent  : tip as an integer percentage (0-100)

The amount to split is the bill plus the tip. The tip is rounded to the
nearest satang (half up) so everything stays in integer satang.
The amount is split evenly; any remainder satang is given one each to the
first people in order.
"""


def split_bill(total, people, tip_percent):
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise ValueError("total must be a non-negative integer (satang)")
    if not isinstance(people, int) or isinstance(people, bool) or people < 1:
        raise ValueError("people must be an integer >= 1")
    if not isinstance(tip_percent, int) or isinstance(tip_percent, bool) \
            or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be an integer between 0 and 100")

    # Tip in satang, rounded half up using integer arithmetic only.
    tip = (total * tip_percent + 50) // 100
    amount = total + tip

    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # 11000 satang / 3 -> [3667, 3667, 3666]
    print(split_bill(0, 4, 0))       # [0, 0, 0, 0]
    print(split_bill(999, 1, 0))     # [999]
