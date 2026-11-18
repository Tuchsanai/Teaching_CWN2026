import json
import subprocess
import sys
import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_1(self):
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_2(self):
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_3(self):
        self.assertEqual(late_fee(200000, 0), 0)


class Boundary(unittest.TestCase):
    def test_3_days_free(self):
        self.assertEqual(late_fee(100000, 3), 0)

    def test_4_days(self):
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_cap_reached_at_20(self):
        self.assertEqual(late_fee(100000, 20), 15000)

    def test_cap_19_20_21(self):
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(100000, 21), 15000)

    def test_max_days_and_zero_amount(self):
        self.assertEqual(late_fee(100000, 365), 15000)
        self.assertEqual(late_fee(0, 100), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 100*4*0.0075 = 3.0 ; 150*4*0.0075 = 4.5 -> 5
        self.assertEqual(late_fee(150, 4), 5)

    def test_half_up_2(self):
        # 10*5*0.0075=0.375 ->0 ; 70*5*0.0075=2.625 -> 3
        self.assertEqual(late_fee(10, 5), 0)
        self.assertEqual(late_fee(70, 5), 3)

    def test_cap_rounding(self):
        # cap 15% of 10 = 1.5 -> 2
        self.assertEqual(late_fee(10, 365), 2)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     ("100", 5), (100, "5"), (True, 5), (100, True), (None, 5)]:
            with self.subTest(a=a, d=d):
                with self.assertRaises(ValueError):
                    late_fee(a, d)

    def test_reject_before_free(self):
        with self.assertRaises(ValueError):
            late_fee(100, 366)


class Cli(unittest.TestCase):
    def run_cli(self, payload):
        p = subprocess.run([sys.executable, "solve.py"], input=json.dumps(payload),
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_ok(self):
        self.assertEqual(self.run_cli({"amount": 100000, "days_late": 4}),
                         (0, {"ok": True, "result": 3000}))

    def test_error(self):
        code, out = self.run_cli({"amount": -1, "days_late": 4})
        self.assertEqual(code, 2)
        self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
