import subprocess, sys, unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", True), 8000)

    def test_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500001, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 20000)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_round(self):
        self.assertEqual(cashback(10010, "silver", False), 150)   # 150.15
        self.assertEqual(cashback(10100, "silver", False), 152)   # 151.5 -> 152
        self.assertEqual(cashback(10020, "gold", False), 251)     # 250.5 -> 251

    def test_reject(self):
        for a in (-1, 1000.0, "3", True, None, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                cashback(a, "gold", False)
        for t in ("bronze", None, ["gold"], 1):
            with self.assertRaises(ValueError):
                cashback(10000, t, False)
        for b in (1, 0, None, "True"):
            with self.assertRaises(ValueError):
                cashback(10000, "gold", b)
        with self.assertRaises(ValueError):
            cashback(-5, "x", 1)
        self.assertEqual(cashback(10**12, "gold", True), 20000)

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], input='{"amount":10100,"tier":"silver","birthday":false}', capture_output=True, text=True)
        self.assertIn('"result": 152', r.stdout)
        r = subprocess.run([sys.executable, "solve.py"], input='{"amount":-1,"tier":"silver","birthday":false}', capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


unittest.main() if __name__ == "__main__" else None
