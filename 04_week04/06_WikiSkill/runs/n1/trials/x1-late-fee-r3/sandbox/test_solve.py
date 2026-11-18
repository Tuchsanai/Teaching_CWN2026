import json
import subprocess
import sys
import unittest

from solve import late_fee


class TestLateFee(unittest.TestCase):
    def test_grace(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)

    def test_normal(self):
        self.assertEqual(late_fee(100000, 4), 3000)
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)
        self.assertEqual(late_fee(100000, 19), 14250)

    def test_half_up(self):
        # 200*4*0.0075 = 6.0 ; 10*4*.0075=0.3 ; 70*4*.0075=2.1; 200*5*.0075=7.5 -> 8
        self.assertEqual(late_fee(200, 5), 8)
        self.assertEqual(late_fee(10, 4), 0)
        self.assertEqual(late_fee(0, 10), 0)

    def test_errors(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     (True, 5), (100, True), ("100", 5), (None, 5)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli('{"amount": 100000, "days_late": 4}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 3000})
        r = self.run_cli('{"amount": 100000.0, "days_late": 4}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)
        r = self.run_cli('not json')
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
