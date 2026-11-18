import json
import subprocess
import sys
import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_1(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_2(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_3(self):
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_4(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)


class Boundary(unittest.TestCase):
    def test_49(self):
        self.assertEqual(bulk_price(10000, 49, False), 505950)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_max_qty(self):
        self.assertEqual(bulk_price(10000, 1000, False), 9897500)

    def test_tier_switch(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5


class NoDrift(unittest.TestCase):
    def test_half_up_coupon(self):
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # 10432.5

    def test_half_up_tier(self):
        self.assertEqual(bulk_price(10000, 49, False), 505950)  # 505949.5


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, 1, False), (100, 0, False), (100, 1001, False), (100.0, 1, False),
                     (100, "2", False), (100, True, False), (True, 1, False), (100, 1, 1),
                     (100, 1, None), (100, 1.0, False)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                bulk_price(*args)


class Cli(unittest.TestCase):
    def run_cli(self, payload):
        p = subprocess.run([sys.executable, "solve.py"], input=json.dumps(payload),
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_ok(self):
        self.assertEqual(self.run_cli({"unit_price": 10000, "qty": 10, "coupon": False}),
                         (0, {"ok": True, "result": 103255}))

    def test_err(self):
        code, out = self.run_cli({"unit_price": 10000, "qty": 0, "coupon": False})
        self.assertEqual(code, 2)
        self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
