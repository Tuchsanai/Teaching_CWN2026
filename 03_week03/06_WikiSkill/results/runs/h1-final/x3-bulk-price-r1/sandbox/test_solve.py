import os
import sys
import json
import unittest
import subprocess

from solve import bulk_price

HERE = os.path.dirname(os.path.abspath(__file__))


class TestBulkPrice(unittest.TestCase):
    # ค่าคาดคำนวณด้วยมือ (ดูหมายเหตุในแต่ละเคส)

    def test_single_bag_no_coupon(self):
        # 10000 * 1 = 10000; * 1.07 = 10700
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_below_first_threshold_no_discount(self):
        # qty 9: 9000 * 1.07 = 9630
        self.assertEqual(bulk_price(1000, 9, False), 9630)

    def test_first_threshold_exact_10_half_up(self):
        # 10000 * 0.965 = 9650; * 1.07 = 10325.5 -> ปัดขึ้น 10326
        self.assertEqual(bulk_price(1000, 10, False), 10326)

    def test_between_thresholds_49(self):
        # 49000 * 0.965 = 47285; * 1.07 = 50594.95 -> 50595
        self.assertEqual(bulk_price(1000, 49, False), 50595)

    def test_second_threshold_exact_50(self):
        # 50000 * 0.925 = 46250; * 1.07 = 49487.5 -> ปัดขึ้น 49488
        self.assertEqual(bulk_price(1000, 50, False), 49488)

    def test_coupon_multi_step_single_rounding(self):
        # 50000 * 0.925 * 0.975 = 45093.75; * 1.07 = 48250.3125 -> 48250
        # ถ้าปัดระหว่างทาง (45094 -> 48251) จะผิด
        self.assertEqual(bulk_price(1000, 50, True), 48250)

    def test_coupon_no_bulk(self):
        # 1000 * 0.975 = 975; * 1.07 = 1043.25 -> 1043
        self.assertEqual(bulk_price(1000, 1, True), 1043)

    def test_upper_bound_qty(self):
        # 1000 * 1000 = 1000000; * 0.925 = 925000; * 1.07 = 989750
        self.assertEqual(bulk_price(1000, 1000, False), 989750)

    def test_zero_price(self):
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_rejects_float_unit_price(self):
        with self.assertRaises(ValueError):
            bulk_price(1000.0, 1, False)

    def test_rejects_bool_unit_price(self):
        with self.assertRaises(ValueError):
            bulk_price(True, 1, False)

    def test_rejects_str_unit_price(self):
        with self.assertRaises(ValueError):
            bulk_price("1000", 1, False)

    def test_rejects_none_unit_price(self):
        with self.assertRaises(ValueError):
            bulk_price(None, 1, False)

    def test_rejects_negative_unit_price(self):
        with self.assertRaises(ValueError):
            bulk_price(-1, 1, False)

    def test_rejects_qty_zero(self):
        with self.assertRaises(ValueError):
            bulk_price(1000, 0, False)

    def test_rejects_qty_over_1000(self):
        with self.assertRaises(ValueError):
            bulk_price(1000, 1001, False)

    def test_rejects_float_qty(self):
        with self.assertRaises(ValueError):
            bulk_price(1000, 10.0, False)

    def test_rejects_bool_qty(self):
        with self.assertRaises(ValueError):
            bulk_price(1000, True, False)

    def test_rejects_str_qty(self):
        with self.assertRaises(ValueError):
            bulk_price(1000, "10", False)

    def test_rejects_none_qty(self):
        with self.assertRaises(ValueError):
            bulk_price(1000, None, False)

    def test_rejects_int_coupon(self):
        with self.assertRaises(ValueError):
            bulk_price(1000, 1, 1)

    def test_rejects_str_coupon(self):
        with self.assertRaises(ValueError):
            bulk_price(1000, 1, "true")

    def test_rejects_none_coupon(self):
        with self.assertRaises(ValueError):
            bulk_price(1000, 1, None)


class TestCli(unittest.TestCase):
    def run_cli(self, payload):
        return subprocess.run(
            [sys.executable, "solve.py"],
            input=payload,
            capture_output=True,
            text=True,
            cwd=HERE,
        )

    def test_cli_ok(self):
        p = self.run_cli(json.dumps({"unit_price": 1000, "qty": 10, "coupon": False}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 10326})

    def test_cli_invalid_input_exit_2(self):
        p = self.run_cli(json.dumps({"unit_price": 1000.0, "qty": 10, "coupon": False}))
        self.assertEqual(p.returncode, 2)
        out = json.loads(p.stdout)
        self.assertFalse(out["ok"])
        self.assertIn("error", out)

    def test_cli_bad_json_exit_2(self):
        p = self.run_cli("{not json")
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
