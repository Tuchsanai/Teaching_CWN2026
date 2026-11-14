import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)

    def test_no_discount(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_threshold_exact(self):
        # 50000*0.95*1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member_only(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_member_and_bulk(self):
        # 100000*0.95*0.9*1.07 = 91485
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 2}], True), 91485)

    def test_half_up(self):
        # 50*1.07=53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        for bad in ([{"price": 1.5, "qty": 1}], [{"price": 1, "qty": 0}],
                    [{"price": True, "qty": 1}], [{"price": 1}], "x"):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)
        with self.assertRaises(ValueError):
            cafe_bill([], 1)


if __name__ == "__main__":
    unittest.main()
