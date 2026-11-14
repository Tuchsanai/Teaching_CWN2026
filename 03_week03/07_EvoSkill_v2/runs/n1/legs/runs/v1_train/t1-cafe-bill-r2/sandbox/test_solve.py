import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], True), 19260)

    def test_boundary(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_rounding(self):
        # 150*1.07 = 160.5 -> 161
        self.assertEqual(cafe_bill([{"price": 150, "qty": 1}], False), 161)

    def test_reject(self):
        bad = [
            ([{"price": 100, "qty": 0}], False),
            ([{"price": 100.0, "qty": 1}], False),
            ([{"price": 100, "qty": "2"}], False),
            ([{"price": True, "qty": 1}], False),
            ([{"price": -1, "qty": 1}], False),
            ([{"price": 100}], False),
            ([{"price": 100, "qty": 1}], 1),
            ([{"price": 100, "qty": 1}], "yes"),
            ("x", False),
            ([5], False),
        ]
        for a, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(a, m)


if __name__ == "__main__":
    unittest.main()
