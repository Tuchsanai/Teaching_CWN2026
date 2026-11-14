import unittest

from solve import cafe_bill


def it(price, qty=1):
    return {"price": price, "qty": qty}


class Normal(unittest.TestCase):
    def test_single(self):
        self.assertEqual(cafe_bill([it(10000)], False), 10700)

    def test_member_below_threshold(self):
        # 10000*0.9*1.07 = 9630
        self.assertEqual(cafe_bill([it(10000)], True), 9630)

    def test_qty_multi_item(self):
        # 25000*2 = 50000 -> *0.95*1.07 = 50825
        self.assertEqual(cafe_bill([it(25000, 2)], False), 50825)

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)


class Boundary(unittest.TestCase):
    def test_below(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)

    def test_at(self):
        self.assertEqual(cafe_bill([it(50000)], False), 50825)

    def test_above(self):
        # 50001*0.95*1.07 = 50825.95 -> 50826
        self.assertEqual(cafe_bill([it(50001)], False), 50826)


class NoDrift(unittest.TestCase):
    def test_half_up_member(self):
        # 50000*0.95*0.9*1.07 = 45742.5 -> 45743
        self.assertEqual(cafe_bill([it(50000)], True), 45743)

    def test_no_intermediate_rounding(self):
        # 4505*0.9*1.07 = 4338.315 -> 4338
        self.assertEqual(cafe_bill([it(4505)], True), 4338)

    def test_returns_int(self):
        self.assertIs(type(cafe_bill([it(4505)], True)), int)


class Reject(unittest.TestCase):
    def test_float_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100.0, "qty": 1}], False)

    def test_str_qty(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": "1"}], False)

    def test_zero_qty(self):
        with self.assertRaises(ValueError):
            cafe_bill([it(100, 0)], False)

    def test_negative_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([it(-1)], False)

    def test_bool_member(self):
        with self.assertRaises(ValueError):
            cafe_bill([], 1)

    def test_bool_qty(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": True}], False)

    def test_missing_key_and_structure(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100}], False)
        with self.assertRaises(ValueError):
            cafe_bill([5], False)
        with self.assertRaises(ValueError):
            cafe_bill("x", False)


if __name__ == "__main__":
    unittest.main()
