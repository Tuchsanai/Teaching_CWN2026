"""BaanKafe coffee-course refund calculator.

refund(paid, used_percent, restock)
    paid         -- amount the customer paid, in satang (integer, >= 0)
    used_percent -- percentage of the course already taken (integer, 0-100)
    restock      -- True means the 12.5% handling fee is deducted

Returns the refund amount in satang (integer).
"""


def refund(paid: int, used_percent: int, restock: bool) -> int:
    if not isinstance(paid, int) or isinstance(paid, bool) or paid < 0:
        raise ValueError("paid must be a non-negative integer (satang)")
    if not isinstance(used_percent, int) or isinstance(used_percent, bool) \
            or not 0 <= used_percent <= 100:
        raise ValueError("used_percent must be an integer between 0 and 100")

    # More than 80% of the course taken: no refund.
    if used_percent > 80:
        return 0

    # Refund is proportional to the unused share: paid * (100 - used) / 100.
    # Handling fee of 12.5% (= 1/8) is deducted when restock is True,
    # leaving 7/8 of the amount: paid * (100 - used) * 7 / 800.
    # All arithmetic is kept in integers; floor division means the
    # customer is never refunded more than the exact value.
    unused = 100 - used_percent
    if restock:
        return paid * unused * 7 // 800
    return paid * unused // 100


if __name__ == "__main__":
    # Quick sanity checks
    assert refund(100_000, 0, False) == 100_000
    assert refund(100_000, 0, True) == 87_500
    assert refund(100_000, 50, False) == 50_000
    assert refund(100_000, 50, True) == 43_750
    assert refund(100_000, 80, False) == 20_000   # exactly 80% still refunds
    assert refund(100_000, 81, False) == 0        # over 80% -> no refund
    assert refund(100_000, 100, True) == 0
    assert refund(0, 10, True) == 0
    assert refund(999, 33, True) == 999 * 67 * 7 // 800  # floored to whole satang
    print("all checks passed")
