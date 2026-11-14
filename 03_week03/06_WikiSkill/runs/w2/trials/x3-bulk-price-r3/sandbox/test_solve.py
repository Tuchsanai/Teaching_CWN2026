import json
import subprocess
import sys
import unittest

from solve import bulk_price


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_boundaries(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)   # 100000*.965*1.07=103255
        self.assertEqual(bulk_price(10000, 49, False), 505950)   # 505949.5 -> up
        self.assertEqual(bulk_price(10000, 50, False), 494875)   # 500000*.925*1.07

    def test_coupon(self):
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # 10000*.975*1.07=10432.5 -> up
        self.assertEqual(bulk_price(10000, 10, True), 100674)  # 100673.625

    def test_invalid(self):
        for args in [(-1, 1, False), (100, 0, False), (100, 1001, False),
                     (100.0, 1, False), (100, 1.0, False), (True, 1, False),
                     (100, True, False), (100, 1, 1), (100, 1, None)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], input='{"unit_price":10000,"qty":1,"coupon":false}',
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 10700})
        r = subprocess.run([sys.executable, "solve.py"], input='{"unit_price":-1,"qty":1,"coupon":false}',
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
