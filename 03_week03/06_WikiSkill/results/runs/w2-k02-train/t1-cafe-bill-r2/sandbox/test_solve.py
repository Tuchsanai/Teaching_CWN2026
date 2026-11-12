import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], True), 19260)
        self.assertEqual(cafe_bill([], False), 0)

    def test_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], False), 50826)

    def test_half_up(self):
        # 5 * 107 / 100 = 5.35 -> 5 ; 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)
        self.assertEqual(cafe_bill([{"price": 5, "qty": 1}], False), 5)

    def test_reject(self):
        bad = [
            ([{"price": 1000.0, "qty": 1}], False),
            ([{"price": 1000, "qty": 0}], False),
            ([{"price": -1, "qty": 1}], False),
            ([{"price": True, "qty": 1}], False),
            ([{"price": 1}], False),
            (["x"], False),
            ("x", False),
            ([], 1),
        ]
        for a in bad:
            with self.assertRaises(ValueError):
                cafe_bill(*a)


if __name__ == "__main__":
    unittest.main()
