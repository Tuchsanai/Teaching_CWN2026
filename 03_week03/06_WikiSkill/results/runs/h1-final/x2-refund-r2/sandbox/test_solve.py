import json
import os
import subprocess
import sys
import unittest

from solve import refund

HERE = os.path.dirname(os.path.abspath(__file__))


class TestRefund(unittest.TestCase):
    # ค่าคาดคำนวณด้วยมือ (ไม่ได้คัดลอกจากฟังก์ชัน)

    def test_no_use_full_refund_no_restock(self):
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_no_use_full_refund_with_restock(self):
        # 10000 * 7/8 = 8750 พอดี
        self.assertEqual(refund(10000, 0, True), 8750)

    def test_proportional_no_restock(self):
        # 10000 * 75% = 7500
        self.assertEqual(refund(10000, 25, False), 7500)

    def test_half_up_on_restock_fee(self):
        # 10000 * 75% = 7500, *7/8 = 6562.5 -> 6563
        self.assertEqual(refund(10000, 25, True), 6563)

    def test_half_up_exact_half_no_restock(self):
        # 5 * 50% = 2.5 -> 3
        self.assertEqual(refund(5, 50, False), 3)

    def test_half_up_small_amount_restock(self):
        # 1 * 100% * 7/8 = 0.875 -> 1
        self.assertEqual(refund(1, 0, True), 1)

    def test_half_up_result_below_one(self):
        # 1 * 50% = 0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)

    def test_single_rounding_multi_step(self):
        # 3 * 50% = 1.5, *7/8 = 1.3125 -> 1 (ปัดทุกขั้นจะได้ 2 ผิด)
        self.assertEqual(refund(3, 50, True), 1)

    def test_single_rounding_multi_step_two(self):
        # 7 * 7/8 = 6.125 -> 6
        self.assertEqual(refund(7, 0, True), 6)

    def test_exact_restock_no_rounding(self):
        # 8 * 7/8 = 7 พอดี
        self.assertEqual(refund(8, 0, True), 7)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 0, True), 0)
        self.assertEqual(refund(0, 50, False), 0)

    def test_cutoff_boundary_80_still_refunds(self):
        # 10000 * 20% = 2000 (เรียน 80% ยังคืน)
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_cutoff_boundary_81_no_refund(self):
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 81, True), 0)

    def test_100_percent_used_no_refund(self):
        self.assertEqual(refund(10000, 100, False), 0)

    def test_reject_float_paid(self):
        with self.assertRaises(ValueError):
            refund(4500.0, 0, False)

    def test_reject_bool_paid(self):
        with self.assertRaises(ValueError):
            refund(True, 0, False)

    def test_reject_none_and_str_paid(self):
        with self.assertRaises(ValueError):
            refund(None, 0, False)
        with self.assertRaises(ValueError):
            refund("100", 0, False)

    def test_reject_negative_paid(self):
        with self.assertRaises(ValueError):
            refund(-1, 0, False)

    def test_reject_float_used_percent(self):
        with self.assertRaises(ValueError):
            refund(10000, 50.0, False)

    def test_reject_bool_used_percent(self):
        with self.assertRaises(ValueError):
            refund(10000, True, False)

    def test_reject_used_percent_out_of_range(self):
        with self.assertRaises(ValueError):
            refund(10000, -1, False)
        with self.assertRaises(ValueError):
            refund(10000, 101, False)

    def test_reject_non_bool_restock(self):
        with self.assertRaises(ValueError):
            refund(10000, 0, 1)
        with self.assertRaises(ValueError):
            refund(10000, 0, None)
        with self.assertRaises(ValueError):
            refund(10000, 0, "yes")


class TestCli(unittest.TestCase):
    def _run(self, payload):
        return subprocess.run(
            [sys.executable, "solve.py"],
            input=payload,
            capture_output=True,
            text=True,
            cwd=HERE,
        )

    def test_cli_success(self):
        p = self._run(json.dumps({"paid": 10000, "used_percent": 25, "restock": True}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 6563})

    def test_cli_invalid_input_exit_2(self):
        p = self._run(json.dumps({"paid": 4500.0, "used_percent": 25, "restock": True}))
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])
        self.assertNotIn("Traceback", p.stderr)

    def test_cli_bad_json_exit_2(self):
        p = self._run("{not json")
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
