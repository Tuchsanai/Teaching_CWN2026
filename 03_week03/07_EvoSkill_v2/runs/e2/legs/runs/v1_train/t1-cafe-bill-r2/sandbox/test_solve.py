import unittest
from solve import cafe_bill as f

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f([{"price": 10000, "qty": 1}], False), 10700)
        self.assertEqual(f([{"price": 10000, "qty": 1}], True), 9630)
    def test_boundary(self):
        self.assertEqual(f([{"price": 49999, "qty": 1}], False), 53499)
        self.assertEqual(f([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(f([{"price": 50000, "qty": 1}], True), 45743)  # 45742.5 half-up
    def test_empty(self):
        self.assertEqual(f([], False), 0)
    def test_reject(self):
        for items, m in [([{"price": 1, "qty": 0}], False), ([{"price": -1, "qty": 1}], False),
                         ([{"price": 1.0, "qty": 1}], False), ([{"price": "1", "qty": 1}], False),
                         ([{"price": True, "qty": 1}], False), ([{"price": 1}], False),
                         ([{"price": 1, "qty": 1}], 1), ("x", False), ([1], False)]:
            with self.assertRaises(ValueError):
                f(items, m)
unittest.main() if __name__ == "__main__" else None
