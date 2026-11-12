import json
import subprocess
import sys
import unittest

from solve import late_fee


class LateFeeTest(unittest.TestCase):
    def test_grace_period(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)

    def test_first_day_over_grace(self):
        self.assertEqual(late_fee(200, 4), 6)

    def test_half_rounds_up(self):
        self.assertEqual(late_fee(20, 10), 2)

    def test_cap(self):
        self.assertEqual(late_fee(1000, 20), 150)
        self.assertEqual(late_fee(1000, 365), 150)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_invalid_inputs(self):
        for a, d in [(-1, 5), (10, -1), (10, 366), (10.0, 5), (10, 5.0),
                     (True, 5), (10, False), ("10", 5), (None, 5)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_cli_ok(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True,
                           text=True, input=json.dumps({"amount": 1000, "days_late": 10}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 75})

    def test_cli_errors(self):
        for inp in ["not json", "{}", json.dumps({"amount": 1, "days_late": 400})]:
            p = subprocess.run([sys.executable, "solve.py"], capture_output=True,
                               text=True, input=inp)
            self.assertEqual(p.returncode, 2)
            self.assertFalse(json.loads(p.stdout)["ok"])
            self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
