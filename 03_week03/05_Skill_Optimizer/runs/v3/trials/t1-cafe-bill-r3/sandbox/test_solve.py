import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)

    def test_threshold_exact(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50000 * 95 * 107 // 10000)

    def test_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), (49999 * 107 * 2 + 100) // 200)

    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_both(self):
        self.assertEqual(cafe_bill([{"price": 30000, "qty": 2}], True), (60000 * 95 * 90 * 107) // 1000000)

    def test_half_up(self):
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)  # 53.5

    def test_invalid(self):
        for items, m in [([{"price": 1.5, "qty": 1}], False), ([{"price": 1, "qty": 0}], False),
                         ([{"price": True, "qty": 1}], False), ([{"price": 1, "qty": 1}], 1)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
