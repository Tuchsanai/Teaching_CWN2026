import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], True), 19260)
        self.assertEqual(cafe_bill([{"price": 6000, "qty": 1}, {"price": 4000, "qty": 2}], False), 14980)

    def test_boundary(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)  # 53498.93
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)  # 50825
        self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], False), 50826)
        self.assertEqual(cafe_bill([], False), 0)

    def test_nodrift(self):
        # 105*... ครึ่งสตางค์: 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)
        self.assertEqual(cafe_bill([{"price": 1, "qty": 1}], True), 1)
        self.assertIs(type(cafe_bill([{"price": 123, "qty": 3}], True)), int)

    def test_reject(self):
        ok = [{"price": 100, "qty": 1}]
        bad = [
            ([{"price": 100, "qty": 0}], False), ([{"price": -1, "qty": 1}], False),
            ([{"price": 100.0, "qty": 1}], False), ([{"price": "1", "qty": 1}], False),
            ([{"price": 100, "qty": True}], False), ([{"price": 100}], False),
            ([5], False), ("x", False), (None, False), (ok, 1), (ok, None), (ok, "yes"),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
