import unittest
from solve import cafe_bill as f

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f([{"price": 10000, "qty": 2}], False), 21400)
        self.assertEqual(f([{"price": 10000, "qty": 2}], True), 19260)
    def test_boundary(self):
        self.assertEqual(f([{"price": 49999, "qty": 1}], False), 53499)
        self.assertEqual(f([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(f([{"price": 50001, "qty": 1}], False), 50826)
    def test_nodrift(self):
        # 50000*.95*.9*1.07 = 45739.5*... check exact half-up
        self.assertEqual(f([{"price": 50000, "qty": 1}], True), 45743)  # exactly 45742.5 -> half up
        self.assertEqual(f([{"price": 1, "qty": 1}], False), 1)
        self.assertEqual(f([{"price": 5, "qty": 10}], False), 54)
    def test_reject(self):
        bad = [([{"price": 1.0, "qty": 1}], False), ([{"price": -1, "qty": 1}], False),
               ([{"price": 1, "qty": 0}], False), ([{"price": True, "qty": 1}], False),
               ([{"price": 1, "qty": "1"}], False), ([{"price": 1}], False),
               ([1], False), ("x", False), ([], 1), ([{"price": 1, "qty": 1}], None)]
        for a, m in bad:
            with self.assertRaises(ValueError):
                f(a, m)
if __name__ == "__main__":
    unittest.main()
