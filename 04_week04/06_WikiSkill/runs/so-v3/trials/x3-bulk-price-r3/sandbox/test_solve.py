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

    def test_tier_50(self):
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_coupon_stacks(self):
        # 10000*10*0.965*0.975*1.07 = 100673.625 -> 100674
        self.assertEqual(bulk_price(10000, 10, True), 100674)

    def test_boundaries(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 49, False), 50595)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_half_rounds_up(self):
        self.assertEqual(bulk_price(50, 1, False), 54)

    def test_invalid(self):
        for args in [(-1, 1, False), (1, 0, False), (1, 1001, False),
                     (1.5, 1, False), (True, 1, False), (1, 1, 1),
                     ("1", 1, False), (1, None, True)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True,
                           text=True,
                           input=json.dumps({"unit_price": 10000, "qty": 10, "coupon": True}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 100674})
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True,
                           text=True, input="oops")
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
