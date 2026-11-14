import json
import subprocess
import sys
import unittest

from solve import bulk_price


class TestBulkPrice(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(100, 1, False), 107)
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_tiers(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)    # 9000*1.07
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5 -> up
        self.assertEqual(bulk_price(1000, 49, False), 50595)  # 47285*1.07=50594.95
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # 49487.5 -> up

    def test_coupon(self):
        self.assertEqual(bulk_price(1000, 50, True), 48250)   # 48250.3125
        self.assertEqual(bulk_price(1000, 1, True), 1043)     # 1042.9 -> 1043

    def test_invalid(self):
        for args in [(-1, 1, False), (100, 0, False), (100, 1001, False),
                     (100.0, 1, False), (100, 1.0, False), (True, 1, False),
                     (100, True, False), (100, 1, 1), (100, 1, "yes"),
                     ("100", 1, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def _cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli_ok(self):
        r = self._cli('{"unit_price": 100, "qty": 1, "coupon": false}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 107})

    def test_cli_error(self):
        r = self._cli('{"unit_price": -5, "qty": 1, "coupon": false}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
