import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_basic_vat(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)

    def test_threshold_exact(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_both(self):
        self.assertEqual(cafe_bill([{"price": 25000, "qty": 2}], True), 45743)

    def test_half_up(self):
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        for bad in ([{"price": 1.5, "qty": 1}], [{"price": 1, "qty": 0}],
                    [{"price": True, "qty": 1}], "x"):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)
        with self.assertRaises(ValueError):
            cafe_bill([], 1)


if __name__ == "__main__":
    unittest.main()
