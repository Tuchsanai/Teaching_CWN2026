import json
import subprocess
import sys
import unittest

from solve import late_fee


class TestLateFee(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_boundaries(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 4), 3000)
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(0, 50), 0)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_half_up(self):
        # 200*4*0.0075 = 6.0 ; 2*4*.0075... use 50*10*.0075=3.75 -> 4
        self.assertEqual(late_fee(50, 10), 4)
        # 2*0.0075*... amount=200,d=4 -> 6.0 ; amount=10,d=4 -> 0.3 -> 0
        self.assertEqual(late_fee(10, 4), 0)
        # 0.5 exactly: amount=200/3 not int; amount=100,d=... 100*75*d/10000=0.75d; d=2 skipped; d=14 ->10.5 -> 11
        self.assertEqual(late_fee(100, 14), 11)

    def test_errors(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     (True, 5), (100, True), ("100", 5), (None, 5), (100, "5")]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def run_cli(self, text):
        return subprocess.run([sys.executable, "solve.py"], input=text,
                              capture_output=True, text=True)

    def test_cli_ok(self):
        p = self.run_cli('{"amount": 100000, "days_late": 10}')
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 7500})

    def test_cli_errors(self):
        for t in ['{"amount": 100.0, "days_late": 10}', '{"amount": 1}',
                  'not json', '[1]', '{"amount": 1, "days_late": 400}']:
            p = self.run_cli(t)
            self.assertEqual(p.returncode, 2)
            self.assertFalse(json.loads(p.stdout)["ok"])
            self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
