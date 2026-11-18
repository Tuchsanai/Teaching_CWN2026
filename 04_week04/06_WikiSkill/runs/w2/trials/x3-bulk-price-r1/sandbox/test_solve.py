import json, subprocess, sys, unittest
from solve import bulk_price


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_tiers(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 10, False), 103255)
        self.assertEqual(bulk_price(10000, 49, False), 505950)  # .5 ปัดขึ้น
        self.assertEqual(bulk_price(10000, 50, False), 494875)
        self.assertEqual(bulk_price(10000, 1000, False), 9897500)

    def test_coupon(self):
        self.assertEqual(bulk_price(10000, 1, True), 10433)  # 10432.5
        self.assertEqual(bulk_price(10000, 10, True), 100674)
        self.assertEqual(bulk_price(10000, 50, True), 482503)  # 482503.125

    def test_rounding(self):
        self.assertEqual(bulk_price(1, 1, False), 1)
        self.assertEqual(bulk_price(5, 1, False), 5)

    def test_invalid(self):
        for args in [(-1, 1, False), (100, 0, False), (100, 1001, False),
                     (100.0, 1, False), (100, 1.0, False), (True, 1, False),
                     (100, True, False), (100, 1, 1), (100, 1, "x"),
                     ("100", 1, False), (None, 1, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli('{"unit_price":10000,"qty":10,"coupon":false}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 103255})
        r = self.run_cli('{"unit_price":-5,"qty":10,"coupon":false}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
