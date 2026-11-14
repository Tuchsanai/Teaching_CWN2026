import json
import subprocess
import sys
import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_1(self):
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_2(self):
        self.assertEqual(late_fee(200000, 4), 6000)

    def test_3(self):
        self.assertEqual(late_fee(100000, 0), 0)


class Boundary(unittest.TestCase):
    def test_3_days_free(self):
        self.assertEqual(late_fee(100000, 3), 0)

    def test_4_days(self):
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_cap_exact_20(self):
        self.assertEqual(late_fee(100000, 20), 15000)

    def test_cap_21(self):
        self.assertEqual(late_fee(100000, 21), 15000)

    def test_max_days(self):
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 50), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(late_fee(100, 5), 4)   # 3.75 -> 4

    def test_below_half(self):
        self.assertEqual(late_fee(10, 10), 1)   # 0.75 -> 1

    def test_exact_half(self):
        self.assertEqual(late_fee(20, 10), 2)   # 1.5 -> 2

    def test_floor_differs(self):
        self.assertEqual(late_fee(1000, 4), 30)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     ("100", 5), (100, "5"), (True, 5), (100, True), (None, 5)]:
            with self.subTest(a=a, d=d):
                with self.assertRaises(ValueError):
                    late_fee(a, d)


class Cli(unittest.TestCase):
    def run_cli(self, payload):
        p = subprocess.run([sys.executable, "solve.py"], input=json.dumps(payload),
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_ok(self):
        self.assertEqual(self.run_cli({"amount": 100000, "days_late": 10}),
                         (0, {"ok": True, "result": 7500}))

    def test_err(self):
        code, out = self.run_cli({"amount": -1, "days_late": 10})
        self.assertEqual(code, 2)
        self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
