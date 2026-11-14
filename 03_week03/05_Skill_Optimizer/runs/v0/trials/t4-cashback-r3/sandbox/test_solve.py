import json, subprocess, sys, unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_birthday(self):
        self.assertEqual(cashback(10000, "gold", True), 500)

    def test_cap(self):
        self.assertEqual(cashback(10_000_00, "platinum", False), 20000)
        self.assertEqual(cashback(500_000, "platinum", False), 20000)
        self.assertEqual(cashback(500_000, "gold", True), 20000)

    def test_rounding(self):
        self.assertEqual(cashback(10001, "silver", False), 150)   # 150.015
        self.assertEqual(cashback(10033, "silver", False), 150)   # 150.495
        self.assertEqual(cashback(10034, "silver", False), 151)   # 150.51
        self.assertEqual(cashback(10010, "silver", False), 150)   # 150.15
        self.assertEqual(cashback(10100, "silver", False), 152)   # 151.5 -> half up
        self.assertIsInstance(cashback(12345, "gold", True), int)

    def test_invalid(self):
        for args in [(-1, "gold", False), (1.5, "gold", False), ("100", "gold", False),
                     (True, "gold", False), (10000, "bronze", False), (10000, "gold", 1),
                     (10000, None, False)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py", json.dumps(
            {"amount": 10000, "tier": "gold", "birthday": True})], capture_output=True, text=True)
        self.assertEqual(json.loads(p.stdout), {"cashback": 500})
        p = subprocess.run([sys.executable, "solve.py"], input='{"amount":-5,"tier":"gold","birthday":false}',
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)
        self.assertIn("error", json.loads(p.stdout))


if __name__ == "__main__":
    unittest.main()
