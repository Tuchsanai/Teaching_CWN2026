import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_threshold(self):
        # 49999 -> no discount: 49999*1.07 = 53498.93
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        # 50000 -> 5%: 50000*.95*1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], False), 50826)

    def test_member(self):
        # 50000*.95*.9*1.07 = 45742.5 -> 45743
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_half_up(self):
        # 50*1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        for items, m in [
            ([{"price": 100, "qty": 0}], False),
            ([{"price": 100.0, "qty": 1}], False),
            ([{"price": True, "qty": 1}], False),
            ([{"price": -1, "qty": 1}], False),
            ([{"price": 100}], False),
            ("x", False),
            ([{"price": 100, "qty": 1}], 1),
        ]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
