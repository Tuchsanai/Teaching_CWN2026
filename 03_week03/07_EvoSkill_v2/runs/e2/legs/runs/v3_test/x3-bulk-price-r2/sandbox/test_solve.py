import json
import subprocess
import sys
import unittest

from solve import bulk_price


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(bulk_price(1000, 1, False), 1070)
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5 -> half-up
        self.assertEqual(bulk_price(1000, 50, True), 48250)

    def test_boundary(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)
        self.assertEqual(bulk_price(10000, 49, False), 505950)  # 505949.5 -> half-up
        self.assertEqual(bulk_price(10000, 50, False), 494875)
        self.assertEqual(bulk_price(0, 1, True), 0)
        self.assertEqual(bulk_price(1, 1000, False), 990)  # 925*1.07=989.75

    def test_reject(self):
        for a in [(-1, 1, False), (1, 0, False), (1, 1001, False), (1.0, 1, False),
                  ("1", 1, False), (True, 1, False), (1, 1.0, False), (1, True, False),
                  (None, 1, False), (float("nan"), 1, False), (1, 1, 1), (1, 1, None)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)

    def test_big(self):
        self.assertIsInstance(bulk_price(10**12, 1000, True), int)

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], input=json.dumps({"unit_price": 1000, "qty": 10, "coupon": False}), capture_output=True, text=True)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 10326})
        r = subprocess.run([sys.executable, "solve.py"], input='{"unit_price": -1, "qty": 1, "coupon": false}', capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
