import json
import subprocess
import sys
import unittest

from solve import bulk_price


class TestBulkPrice(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_tier_10(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_tier_50_single_rate(self):
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_coupon(self):
        # 10000*0.975*1.07 = 10432.5 -> half up
        self.assertEqual(bulk_price(10000, 1, True), 10433)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_boundaries(self):
        self.assertEqual(bulk_price(100, 9, False), 963)
        self.assertEqual(bulk_price(100, 49, True), 4933)

    def test_invalid(self):
        for args in [(-1, 1, False), (100, 0, False), (100, 1001, False),
                     (1.5, 1, False), (100, True, False), (100, 1, 1),
                     (None, 1, False), ("1", 1, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"unit_price": 10000, "qty": 1, "coupon": False}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 10700})
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True, input="x")
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
