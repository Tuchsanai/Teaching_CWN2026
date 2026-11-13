import unittest
from solve import cafe_bill as f

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f([{"price": 10000, "qty": 2}], False), 21400)
        self.assertEqual(f([{"price": 10000, "qty": 2}], True), 19260)
        self.assertEqual(f([{"price": 10000, "qty": 5}], False), 50825)
        self.assertEqual(f([{"price": 10000, "qty": 5}], True), 45743)  # 45742.5 half-up
        self.assertEqual(f([], False), 0)
    def test_boundary(self):
        self.assertEqual(f([{"price": 49999, "qty": 1}], False), 53499)
        self.assertEqual(f([{"price": 50000, "qty": 1}], False), 50825)
    def test_reject(self):
        for bad in ([{"price": 1, "qty": 0}], [{"price": -1, "qty": 1}], [{"price": 1.0, "qty": 1}],
                    [{"price": "1", "qty": 1}], [{"price": True, "qty": 1}], [{"price": 1}], [5], None):
            with self.assertRaises(ValueError): f(bad, False)
        with self.assertRaises(ValueError): f([], 1)
unittest.main() if __name__ == "__main__" else None
