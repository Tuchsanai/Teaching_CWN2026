import json
import subprocess
import sys
import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_1(self):
        self.assertEqual(bulk_price(35000, 1, False), 37450)

    def test_2(self):
        self.assertEqual(bulk_price(35000, 10, False), 361393)

    def test_3(self):
        self.assertEqual(bulk_price(35000, 50, True), 1688761)

    def test_4(self):
        self.assertEqual(bulk_price(12345, 7, False), 92464)


class Boundary(unittest.TestCase):
    def test_9_vs_10(self):
        self.assertEqual(bulk_price(35000, 9, False), 337050)
        self.assertEqual(bulk_price(35000, 10, False), 361393)

    def test_49_vs_50(self):
        self.assertEqual(bulk_price(35000, 49, False), 1770823)
        self.assertEqual(bulk_price(35000, 50, False), 1732063)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_max_qty(self):
        self.assertEqual(bulk_price(999, 1000, True), 964041)

    def test_coupon_10(self):
        self.assertEqual(bulk_price(35000, 10, True), 352358)


class NoDrift(unittest.TestCase):
    def test_1(self):
        self.assertEqual(bulk_price(333, 10, True), 3352)

    def test_2(self):
        self.assertEqual(bulk_price(4505, 1, True), 4700)

    def test_3(self):
        self.assertEqual(bulk_price(1, 50, True), 48)


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, 1, False), (100, 0, False), (100, 1001, False), (100, -1, False),
               (100.0, 1, False), (100, 1.0, False), ("100", 1, False), (100, "1", False),
               (True, 1, False), (100, True, False), (100, 1, 1), (100, 1, "yes"),
               (100, 1, None)]
        for args in bad:
            with self.subTest(args=args), self.assertRaises(ValueError):
                bulk_price(*args)


class Cli(unittest.TestCase):
    def run_cli(self, payload):
        p = subprocess.run([sys.executable, "solve.py"], input=json.dumps(payload),
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_ok(self):
        self.assertEqual(self.run_cli({"unit_price": 35000, "qty": 10, "coupon": False}),
                         (0, {"ok": True, "result": 361393}))

    def test_error(self):
        code, out = self.run_cli({"unit_price": 35000, "qty": 0, "coupon": False})
        self.assertEqual(code, 2)
        self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
