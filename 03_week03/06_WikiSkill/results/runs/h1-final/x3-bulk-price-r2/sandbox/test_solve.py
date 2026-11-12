import json
import subprocess
import sys
import unittest

from solve import bulk_price


class TestBulkPrice(unittest.TestCase):
    # ค่าที่คาดคำนวณด้วยมือ (ราคา × จำนวน × ส่วนลด × 1.07 แล้วปัดครั้งเดียว)

    def test_single_bag_no_coupon_only_vat(self):
        # 10000 × 1 × 1.07 = 10700
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_threshold_10_bags_inclusive(self):
        # 9 ถุง ไม่ลด: 90000 × 1.07 = 96300
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        # 10 ถุง ลด 3.5%: 100000 × 0.965 × 1.07 = 103255
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_threshold_50_bags_uses_single_rate(self):
        # 49 ถุง ลด 3.5%: 490000 × 0.965 × 1.07 = 505949.5 -> 505950 (half up)
        self.assertEqual(bulk_price(10000, 49, False), 505950)
        # 50 ถุง ลด 7.5% (อัตราเดียว ไม่ซ้อน): 500000 × 0.925 × 1.07 = 494875
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_coupon_applies_after_bulk_discount(self):
        # 10 ถุง + คูปอง: 100000 × 0.965 × 0.975 × 1.07 = 100673.625 -> 100674
        self.assertEqual(bulk_price(10000, 10, True), 100674)
        # 50 ถุง + คูปอง: 500000 × 0.925 × 0.975 × 1.07 = 482503.125 -> 482503
        self.assertEqual(bulk_price(10000, 50, True), 482503)

    def test_half_up_exact_point_five_rounds_up(self):
        # 50 × 1.07 = 53.5 -> 54 (half up)
        self.assertEqual(bulk_price(50, 1, False), 54)

    def test_single_rounding_at_end(self):
        # 10 ถุงของราคา 1 สตางค์ + คูปอง: 10 × 0.965 × 0.975 × 1.07 = 10.0673625 -> 10
        self.assertEqual(bulk_price(1, 10, True), 10)

    def test_rejects_float_price(self):
        with self.assertRaises(ValueError):
            bulk_price(4500.0, 1, False)

    def test_rejects_negative_price(self):
        with self.assertRaises(ValueError):
            bulk_price(-1, 1, False)

    def test_rejects_bool_price(self):
        with self.assertRaises(ValueError):
            bulk_price(True, 1, False)

    def test_rejects_str_and_none_price(self):
        with self.assertRaises(ValueError):
            bulk_price("100", 1, False)
        with self.assertRaises(ValueError):
            bulk_price(None, 1, False)

    def test_rejects_qty_out_of_range(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 0, False)
        with self.assertRaises(ValueError):
            bulk_price(100, 1001, False)

    def test_accepts_qty_boundaries(self):
        self.assertIsInstance(bulk_price(100, 1, False), int)
        self.assertIsInstance(bulk_price(100, 1000, False), int)

    def test_rejects_float_and_bool_qty(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 1.0, False)
        with self.assertRaises(ValueError):
            bulk_price(100, True, False)

    def test_rejects_non_bool_coupon(self):
        with self.assertRaises(ValueError):
            bulk_price(100, 1, 1)
        with self.assertRaises(ValueError):
            bulk_price(100, 1, "yes")
        with self.assertRaises(ValueError):
            bulk_price(100, 1, None)


class TestCli(unittest.TestCase):
    def _run(self, payload):
        return subprocess.run(
            [sys.executable, "solve.py"],
            input=payload,
            capture_output=True,
            text=True,
        )

    def test_cli_ok(self):
        r = self._run(json.dumps({"unit_price": 10000, "qty": 10, "coupon": True}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 100674})

    def test_cli_error(self):
        r = self._run(json.dumps({"unit_price": 4500.0, "qty": 1, "coupon": False}))
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
