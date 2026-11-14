import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], True), 19260)

    def test_boundary(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        # 50000*0.95*1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_nodrift(self):
        # 105*0.9*1.07 = 101.115 -> 101
        self.assertEqual(cafe_bill([{"price": 105, "qty": 1}], True), 101)
        # 50 *1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_reject(self):
        ok = [{"price": 100, "qty": 1}]
        bad = [
            (ok, 1), (ok, None), ("x", False), (None, False),
            ([1], False), ([{"price": 100}], False), ([{"qty": 1}], False),
            ([{"price": 100.0, "qty": 1}], False), ([{"price": "1", "qty": 1}], False),
            ([{"price": True, "qty": 1}], False), ([{"price": None, "qty": 1}], False),
            ([{"price": -1, "qty": 1}], False), ([{"price": 100, "qty": 0}], False),
            ([{"price": 100, "qty": 1.0}], False), ([{"price": 100, "qty": True}], False),
        ]
        for i, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(i, m)


if __name__ == "__main__":
    unittest.main()
