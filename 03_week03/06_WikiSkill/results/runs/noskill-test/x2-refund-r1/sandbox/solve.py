def refund(paid, used_percent, restock):
    """Refund in satang (integer). Exact integer math, no float error."""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)  # /100
    den = 100
    if restock:  # deduct 12.5% -> keep 7/8
        num *= 7
        den *= 8
    return (2 * num + den) // (2 * den)  # round half up


if __name__ == "__main__":
    assert refund(10000, 50, False) == 5000
    assert refund(10000, 50, True) == 4375
    assert refund(10000, 81, False) == 0
    assert refund(10000, 80, True) == 1750
    assert refund(0, 10, True) == 0
