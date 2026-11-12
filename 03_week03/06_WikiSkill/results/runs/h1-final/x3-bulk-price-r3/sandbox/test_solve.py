import json
import subprocess
import sys
import unittest

from solve import bulk_price


class TestBulkPrice(unittest.TestCase):
    # ค่าคาดคำนวณด้วยมือ (หน่วยสตางค์)

    def test_single_bag_no_discount_no_coupon(self):
        # 10000 * 1.07 = 10700
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_tier_boundary_below_10(self):
        # qty 9 ยังไม่ลด: 90000 * 1.07 = 96300
        self.assertEqual(bulk_price(10000, 9, False), 96300)

    def test_tier_boundary_at_10(self):
        # qty 10 ลด 3.5%: 100000 * 0.965 * 1.07 = 103255
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_tier_just_below_50(self):
        # qty 49 ยังลด 3.5% (ไม่ใช่ 7.5%): 490000 * 0.965 * 1.07 = 505949.5 -> 505950
        self.assertEqual(bulk_price(10000, 49, False), 505950)

    def test_tier_at_50(self):
        # qty 50 ลด 7.5%: 500000 * 0.925 * 1.07 = 494875
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_coupon_stacks_multiplicatively(self):
        # qty 50 + คูปอง: 500000 * 0.925 * 0.975 * 1.07 = 482503.125 -> 482503
        self.assertEqual(bulk_price(10000, 50, True), 482503)

    def test_coupon_single_bag(self):
        # qty 1 + คูปอง: 2000 * 0.975 * 1.07 = 2086.5 -> 2087 (half up)
        self.assertEqual(bulk_price(2000, 1, True), 2087)

    def test_half_up_exact_point_five_with_tier(self):
        # qty 10: 10000 * 0.965 * 1.07 = 10325.5 -> 10326
        self.assertEqual(bulk_price(1000, 10, False), 10326)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 1000, True), 0)

    def test_max_qty(self):
        # 10000 * 1000 * 0.925 * 0.975 * 1.07 = 9650062.5 -> 9650063
        self.assertEqual(bulk_price(10000, 1000, True), 9650063)

    def test_rejects_float_price(self):
        with self.assertRaises(ValueError):
            bulk_price(4500.0, 1, False)

    def test_rejects_bool_in_int_fields(self):
        with self.assertRaises(ValueError):
            bulk_price(True, 1, False)
        with self.assertRaises(ValueError):
            bulk_price(100, True, False)

    def test_rejects_none_and_str(self):
        with self.assertRaises(ValueError):
            bulk_price(None, 1, False)
        with self.assertRaises(ValueError):
            bulk_price(100, "1", False)
        with self.assertRaises(ValueError):
            bulk_price(100, 1, None)

    def test_rejects_negative_price(self):
        with self.assertRaises(ValueError):
            bulk_price(-1, 1, False)

    def test_rejects_qty_out_of_range(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 0, False)
        with self.assertRaises(ValueError):
            bulk_price(100, 1001, False)

    def test_rejects_non_bool_coupon(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 1, 1)
        with self.assertRaises(ValueError):
            bulk_price(100, 1, "yes")


class TestCli(unittest.TestCase):
    def _run(self, payload):
        return subprocess.run(
            [sys.executable, "solve.py"],
            input=payload,
            capture_output=True,
            text=True,
        )

    def test_cli_ok(self):
        r = self._run(json.dumps({"unit_price": 10000, "qty": 10, "coupon": False}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 103255})

    def test_cli_error(self):
        r = self._run(json.dumps({"unit_price": 4500.0, "qty": 1, "coupon": False}))
        self.assertEqual(r.returncode, 2)
        out = json.loads(r.stdout)
        self.assertFalse(out["ok"])
        self.assertIn("error", out)

    def test_cli_bad_json(self):
        r = self._run("{not json")
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
