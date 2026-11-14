import unittest

from solve import cafe_bill


def one(price, member=False, qty=1):
    return cafe_bill([{"price": price, "qty": qty}], member)


class Normal(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(one(10000), 10700)

    def test_member(self):
        self.assertEqual(one(10000, True), 9630)

    def test_multi_items(self):
        # 2*20000 + 10000 = 50000 -> 47500 -> 50825
        self.assertEqual(cafe_bill([{"price": 20000, "qty": 2}, {"price": 10000, "qty": 1}], False), 50825)

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)


class Boundary(unittest.TestCase):
    def test_below(self):
        self.assertEqual(one(49999), 53499)

    def test_at(self):
        self.assertEqual(one(50000), 50825)

    def test_qty_reaches_threshold(self):
        self.assertEqual(one(25000, qty=2), 50825)


class NoDrift(unittest.TestCase):
    def test_half_member(self):  # 500*0.963 = 481.5 -> 482
        self.assertEqual(one(500, True), 482)

    def test_half_plain(self):  # 50*1.07 = 53.5 -> 54
        self.assertEqual(one(50), 54)

    def test_half_discount_member(self):  # 50000*.95*.9*1.07 = 45742.5 -> 45743
        self.assertEqual(one(50000, True), 45743)


class Reject(unittest.TestCase):
    def test_float(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100.0, "qty": 1}], False)

    def test_str_qty(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": "1"}], False)

    def test_qty_zero(self):
        with self.assertRaises(ValueError):
            one(100, qty=0)

    def test_negative_price(self):
        with self.assertRaises(ValueError):
            one(-1)

    def test_bool_member(self):
        with self.assertRaises(ValueError):
            cafe_bill([], 1)

    def test_bool_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": True, "qty": 1}], False)

    def test_missing_key(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100}], False)

    def test_bad_structure(self):
        with self.assertRaises(ValueError):
            cafe_bill("x", False)
        with self.assertRaises(ValueError):
            cafe_bill([5], False)


if __name__ == "__main__":
    unittest.main()
