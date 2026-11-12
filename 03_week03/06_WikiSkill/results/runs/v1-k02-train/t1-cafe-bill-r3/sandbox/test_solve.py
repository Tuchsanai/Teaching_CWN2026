import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_threshold_exact(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_half_up(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        bad = [
            ([{"price": 100, "qty": 0}], False),
            ([{"price": -1, "qty": 1}], False),
            ([{"price": 100.0, "qty": 1}], False),
            ([{"price": 100, "qty": True}], False),
            ([{"price": 100}], False),
            ([1], False),
            ({}, False),
            ([{"price": 100, "qty": 1}], 1),
            ([{"price": 100, "qty": 1}], None),
        ]
        for a in bad:
            with self.assertRaises(ValueError):
                cafe_bill(*a)


if __name__ == "__main__":
    unittest.main()
