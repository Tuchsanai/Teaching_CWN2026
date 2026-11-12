import json
import subprocess
import sys
import unittest

from solve import late_fee


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_threshold(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 4), 3000)
        self.assertEqual(late_fee(100000, 0), 0)

    def test_half_up(self):
        # 200 * 0.0075 * 5 = 7.5 -> 8
        self.assertEqual(late_fee(200, 5), 8)
        # 10 * 0.0075 * 10 = 0.75 -> 1
        self.assertEqual(late_fee(10, 10), 1)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(0, 50), 0)

    def test_single_rounding(self):
        # 333 * 0.0075 * 7 = 17.4825 -> 17
        self.assertEqual(late_fee(333, 7), 17)

    def test_invalid(self):
        for a, d in [(1.0, 5), (True, 5), ("1", 5), (None, 5), (-1, 5),
                     (100, 5.0), (100, True), (100, "5"), (100, None),
                     (100, -1), (100, 366)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli('{"amount": 100000, "days_late": 10}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 7500})
        r = self.run_cli('{"amount": 1.5, "days_late": 10}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertEqual(self.run_cli("nope").returncode, 2)


if __name__ == "__main__":
    unittest.main()
