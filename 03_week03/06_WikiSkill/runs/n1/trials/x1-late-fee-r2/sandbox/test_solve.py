import json
import subprocess
import sys
import unittest

from solve import late_fee


def cli(s):
    return subprocess.run([sys.executable, "solve.py"], input=s,
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_grace(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)

    def test_normal(self):
        self.assertEqual(late_fee(100000, 4), 3000)
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_half_up(self):
        self.assertEqual(late_fee(200, 5), 8)    # 7.5 -> 8
        self.assertEqual(late_fee(10, 4), 0)    # 0.3
        self.assertEqual(late_fee(200, 4), 6)
        self.assertEqual(late_fee(1, 20), 0)    # 0.15
        self.assertEqual(late_fee(0, 10), 0)

    def test_errors(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5),
                     (100, 5.0), (True, 5), (100, True), ("1", 5), (None, 1)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_cli(self):
        r = cli('{"amount": 100000, "days_late": 4}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 3000})
        for bad in ['{"amount": 100.0, "days_late": 4}', '{"amount": 1}',
                    'xx', '[1]', '{"amount": 1, "days_late": 999}']:
            r = cli(bad)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])
            self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
