import json
import subprocess
import sys
import unittest

from solve import bulk_price


def cli(s):
    return subprocess.run([sys.executable, "solve.py"], input=s,
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # 10432.5 half up
        self.assertEqual(bulk_price(10000, 50, True), 482503)

    def test_edges(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)
        self.assertEqual(bulk_price(10000, 49, False), 505950)  # 505949.5 half up
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # 49487.5 half up

    def test_half_up(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)
    def test_errors(self):
        for a in [(-1, 1, False), (100, 0, False), (100, 1001, False), (100.0, 1, False),
                  (True, 1, False), (100, True, False), (100, 1, 1), ("1", 1, False), (100, 1.0, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)
    def test_cli(self):
        r = cli('{"unit_price": 10000, "qty": 1, "coupon": false}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 10700})
        r = cli('{"unit_price": 100.0, "qty": 1, "coupon": false}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
