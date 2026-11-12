import pytest
from solve import cafe_bill


def test_basic_vat():
    assert cafe_bill([{"price": 10000, "qty": 1}], False) == 10700


def test_threshold_discount():
    assert cafe_bill([{"price": 50000, "qty": 1}], False) == 50825  # 47500*1.07
    assert cafe_bill([{"price": 49999, "qty": 1}], False) == 53499


def test_member():
    assert cafe_bill([{"price": 10000, "qty": 1}], True) == 9630


def test_both():
    assert cafe_bill([{"price": 60000, "qty": 1}], True) == 54891  # 51300*1.07


def test_qty_multiplies():
    assert cafe_bill([{"price": 25000, "qty": 2}], False) == 50825


def test_rounding_half_up():
    assert cafe_bill([{"price": 50, "qty": 1}], False) == 54  # 53.5 -> 54


def test_empty():
    assert cafe_bill([], False) == 0


@pytest.mark.parametrize("items,member", [
    ("x", False), ([{"price": 1.5, "qty": 1}], False), ([{"price": 1, "qty": 0}], False),
    ([{"price": -1, "qty": 1}], False), ([{"price": 1}], False), ([1], False),
    ([{"price": True, "qty": 1}], False), ([{"price": 1, "qty": 1}], "yes"),
])
def test_invalid(items, member):
    with pytest.raises(ValueError):
        cafe_bill(items, member)
