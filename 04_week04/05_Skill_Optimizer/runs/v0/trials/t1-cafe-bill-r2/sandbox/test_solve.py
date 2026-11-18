import pytest
from solve import cafe_bill


def test_basic_no_discount():
    assert cafe_bill([{"price": 10000, "qty": 1}], False) == 10700

def test_threshold_exact():
    assert cafe_bill([{"price": 50000, "qty": 1}], False) == 50000 * 95 * 107 // 10000

def test_below_threshold():
    assert cafe_bill([{"price": 49999, "qty": 1}], False) == round(49999 * 1.07)

def test_member_and_bulk():
    assert cafe_bill([{"price": 50000, "qty": 2}], True) == 91485

def test_rounding_half_up():
    assert cafe_bill([{"price": 50, "qty": 1}], False) == 54  # 53.5 -> 54

def test_empty():
    assert cafe_bill([], True) == 0

@pytest.mark.parametrize("items,member", [
    ([{"price": 1, "qty": 0}], False),
    ([{"price": 1.5, "qty": 1}], False),
    ([{"price": -1, "qty": 1}], False),
    ([{"price": 1}], False),
    ("x", False),
    ([{"price": 1, "qty": 1}], "yes"),
])
def test_invalid(items, member):
    with pytest.raises(ValueError):
        cafe_bill(items, member)
