from fractions import Fraction

_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}


def cashback(amount, tier, birthday):
    # validate everything first
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be int >= 0")
    if type(tier) is not str or tier not in _RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < 10000:
        return 0
    x = amount * _RATES[tier]
    # Policy C1 (baankafe-known-policies): birthday x2 only for gold/platinum
    if birthday and tier != "silver":
        x *= 2
    # Policy C2: store pays out -> floor; cap 200 baht applied last
    return min(20000, int(x // 1))


if __name__ == "__main__":
    assert cashback(20000, "silver", False) == 300
    assert cashback(20000, "platinum", True) == 1600
    assert cashback(10015, "platinum", True) == 801
    assert cashback(10020, "gold", True) == 501
    assert cashback(500000, "platinum", False) == 20000
    assert cashback(9999, "gold", False) == 0
    print("ok")
