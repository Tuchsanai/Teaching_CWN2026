import json
import subprocess
import sys
import unittest

from solve import bulk_price


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 9, False), 96300)

    def test_edges(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)  # 100000*.965*1.07
        self.assertEqual(bulk_price(10000, 49, False), 505950)  # 505949.5 -> up
        self.assertEqual(bulk_price(10000, 50, False), 494875)  # 500000*.925*1.07
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # 10700*.975=10432.5 -> up

    def test_coupon_combo(self):
        # 500000*.925*.975*1.07 = 482503.125
        self.assertEqual(bulk_price(10000, 50, True), 482503)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_half_up(self):
        self.assertEqual(bulk_price(50, 1, False), 54)  # 53.5

    def test_errors(self):
        for a in [(-1, 1, False), (100, 0, False), (100, 1001, False),
                  (100.0, 1, False), (100, 1.0, False), (True, 1, False),
                  (100, True, False), (100, 1, 1), (100, 1, None), ("1", 1, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli('{"unit_price": 10000, "qty": 1, "coupon": false}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 10700})
        for s in ['{"unit_price": 100.0, "qty": 1, "coupon": false}', 'bad', '{}', '[]']:
            r = self.run_cli(s)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])
            self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
