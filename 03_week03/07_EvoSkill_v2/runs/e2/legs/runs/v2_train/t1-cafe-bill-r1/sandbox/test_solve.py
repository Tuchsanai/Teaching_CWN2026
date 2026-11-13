import unittest, subprocess, sys
from solve import cafe_bill as f

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f([{"price": 10000, "qty": 2}], False), 21400)
        self.assertEqual(f([], False), 0)
        self.assertEqual(f([{"price": 60000, "qty": 1}], True), 54891)  # 60000*.95*.9*1.07=54891
    def test_boundary(self):
        self.assertEqual(f([{"price": 49999, "qty": 1}], False), 53499)  # 53498.93
        self.assertEqual(f([{"price": 50000, "qty": 1}], False), 50825)
    def test_half(self):
        # 50 *1.07 = 53.5 -> 54 (half-up)
        self.assertEqual(f([{"price": 50, "qty": 1}], False), 54)
    def test_reject(self):
        for bad in [([{"price": -1, "qty": 1}], False), ([{"price": 1, "qty": 0}], False),
                    ([{"price": 1.0, "qty": 1}], False), ([{"price": "1", "qty": 1}], False),
                    ([{"price": True, "qty": 1}], False), ([{"price": 1}], False),
                    ([{"price": 1, "qty": 1}], 1), ([{"price": 1, "qty": 1}], None),
                    (None, False), ([1], False)]:
            with self.assertRaises(ValueError): f(*bad)
    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], input='{"items":[{"price":10000,"qty":2}],"member":false}', capture_output=True, text=True)
        self.assertIn('"result": 21400', r.stdout)
        r = subprocess.run([sys.executable, "solve.py"], input='{"items":[],"member":"x"}', capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
unittest.main() if __name__ == "__main__" else None
