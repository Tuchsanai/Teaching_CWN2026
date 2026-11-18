import unittest
from solve import cafe_bill


class TestCafeBill(unittest.TestCase):
    def test_basic_vat(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)

    def test_threshold_exact(self):
        # 50000 -> 47500 -> 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member(self):
        # 10000*0.9*1.07 = 9630
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_member_and_bulk(self):
        # 100000*.95*.9*1.07 = 91485
        self.assertEqual(cafe_bill([{"price": 25000, "qty": 4}], True), 91485)

    def test_round_half_up_once(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        for items, m in [([{"price": 1.5, "qty": 1}], False),
                         ([{"price": 100, "qty": 0}], False),
                         ([{"price": True, "qty": 1}], False),
                         ([{"price": 100, "qty": 1}], 1),
                         ("x", False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
