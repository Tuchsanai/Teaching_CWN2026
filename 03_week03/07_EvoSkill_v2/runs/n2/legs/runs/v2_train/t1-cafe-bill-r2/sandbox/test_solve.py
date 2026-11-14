import unittest

from solve import cafe_bill


def it(price, qty=1):
    return {"price": price, "qty": qty}


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(cafe_bill([it(100, 2)], False), 214)  # 200*1.07

    def test_normal_2(self):
        self.assertEqual(cafe_bill([it(1000, 3), it(500)], False), 3745)  # 3500*1.07

    def test_normal_3(self):
        self.assertEqual(cafe_bill([it(100, 2)], True), 193)  # 180*1.07=192.6

    def test_empty(self):
        self.assertEqual(cafe_bill([], True), 0)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(cafe_bill([it(50000)], False), 50825)  # 47500*1.07

    def test_boundary_2(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)  # 53498.93

    def test_boundary_3(self):
        self.assertEqual(cafe_bill([it(25000, 2)], True), 45743)  # 42750*1.07=45742.5

    def test_boundary_4(self):
        self.assertEqual(cafe_bill([it(49999)], True), 48149)  # 48149.037


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(cafe_bill([it(1)], True), 1)  # 0.963

    def test_no_drift_2(self):
        self.assertEqual(cafe_bill([it(5)], False), 5)  # 5.35

    def test_no_drift_3(self):
        self.assertEqual(cafe_bill([it(50)], True), 48)  # 48.15

    def test_half_up(self):
        self.assertEqual(cafe_bill([it(50000)], True), 45743)


class Reject(unittest.TestCase):
    def test_reject_negative_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([it(-1)], False)

    def test_reject_qty_zero(self):
        with self.assertRaises(ValueError):
            cafe_bill([it(100, 0)], False)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            cafe_bill([it(100.0)], False)

    def test_reject_str_qty(self):
        with self.assertRaises(ValueError):
            cafe_bill([it(100, "1")], False)

    def test_reject_bool_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([it(True)], False)

    def test_reject_member_type(self):
        with self.assertRaises(ValueError):
            cafe_bill([it(100)], 1)

    def test_reject_missing_key(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100}], False)

    def test_reject_items_type(self):
        with self.assertRaises(ValueError):
            cafe_bill("x", False)


if __name__ == "__main__":
    unittest.main()
