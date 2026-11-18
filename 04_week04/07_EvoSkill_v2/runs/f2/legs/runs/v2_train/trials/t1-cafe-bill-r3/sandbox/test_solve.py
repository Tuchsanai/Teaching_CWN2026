import unittest
from solve import cafe_bill


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], True), 19260)

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)


class Boundary(unittest.TestCase):
    def test_threshold(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_zero_price(self):
        self.assertEqual(cafe_bill([{"price": 0, "qty": 1}], False), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)


class Reject(unittest.TestCase):
    def test_bad(self):
        good = [{"price": 100, "qty": 1}]
        for items, m in [
            ([{"price": -1, "qty": 1}], False), ([{"price": 1, "qty": 0}], False),
            ([{"price": 1.0, "qty": 1}], False), ([{"price": True, "qty": 1}], False),
            ([{"price": 1}], False), ("x", False), ([1], False),
            (good, 1), (good, None),
        ]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
