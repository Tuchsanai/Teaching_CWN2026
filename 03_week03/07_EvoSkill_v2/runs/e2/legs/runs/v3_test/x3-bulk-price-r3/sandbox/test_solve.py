import json
import subprocess
import sys
import unittest
from solve import bulk_price


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 10, False), 103255)
        self.assertEqual(bulk_price(10000, 50, True), 482503)  # 450937.5*1.07=482503.125
        self.assertEqual(bulk_price(5, 10, False), 52)  # 51.6275

    def test_boundary(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5 half-up
        self.assertEqual(bulk_price(1000, 49, False), 50595)  # 50594.95
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # 49487.5 half-up

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_reject(self):
        for a in [(-1, 1, False), (1, 0, False), (1, 1001, False), (1.0, 1, False),
                  ("1", 1, False), (True, 1, False), (1, 1.0, False), (1, True, False),
                  (None, 1, False), (1, 1, 1), (1, 1, None), (float("nan"), 1, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)

    def test_big(self):
        self.assertIsInstance(bulk_price(10**12, 1000, True), int)

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], input='{"unit_price":10000,"qty":1,"coupon":false}',
                           capture_output=True, text=True)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 10700})
        r = subprocess.run([sys.executable, "solve.py"], input='{"unit_price":-1,"qty":1,"coupon":false}',
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
