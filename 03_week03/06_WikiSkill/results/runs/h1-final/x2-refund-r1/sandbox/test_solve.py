import json
import subprocess
import sys
import unittest

from solve import refund


def run_cli(payload_text):
    return subprocess.run(
        [sys.executable, "solve.py"],
        input=payload_text,
        capture_output=True,
        text=True,
    )


class TestRefund(unittest.TestCase):
    # เคสปกติ
    def test_no_usage_no_restock(self):
        # 10000 * 100/100 = 10000
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_proportional(self):
        # 10000 * 70/100 = 7000
        self.assertEqual(refund(10000, 30, False), 7000)

    def test_restock_deduction(self):
        # 10000 * 80/100 = 8000; หัก 12.5% -> 8000 * 7/8 = 7000
        self.assertEqual(refund(10000, 20, True), 7000)

    # ขอบเขตเกณฑ์ 80%
    def test_exactly_80_percent_still_refunds(self):
        # 10000 * 20/100 = 2000
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_81_percent_no_refund(self):
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 81, True), 0)

    def test_100_percent_no_refund(self):
        self.assertEqual(refund(10000, 100, False), 0)

    def test_79_percent_refunds(self):
        # 10000 * 21/100 = 2100
        self.assertEqual(refund(10000, 79, False), 2100)

    # ปัดเศษ half up (.5 ปัดขึ้น)
    def test_half_rounds_up_without_restock(self):
        # 5 * 50/100 = 5/2 = 2.5 -> 3
        self.assertEqual(refund(5, 50, False), 3)

    def test_half_rounds_up_restock_path(self):
        # 2 * 50/100 = 1; หัก 12.5% -> 1 * 7/8 = 0.875 -> 1
        self.assertEqual(refund(2, 50, True), 1)

    def test_below_half_rounds_down(self):
        # 1 * 50/100 = 1/2; * 7/8 = 7/16 = 0.4375 -> 0
        self.assertEqual(refund(1, 50, True), 0)

    # ปัดครั้งเดียวตอนท้าย (ไม่ปัดระหว่างทาง)
    def test_single_rounding_multi_step(self):
        # 3 * 50/100 = 3/2; * 7/8 = 21/16 = 1.3125 -> 1
        # ถ้าปัดกลางทาง (1.5 -> 2) แล้ว *7/8 = 1.75 -> 2 จะผิด
        self.assertEqual(refund(3, 50, True), 1)

    def test_single_rounding_avoids_drift(self):
        # 7 * 70/100 = 49/10 = 4.9; * 7/8 = 343/80 = 4.2875 -> 4
        self.assertEqual(refund(7, 30, True), 4)
        # 5 * 30/100 = 3/2 = 1.5 (ปัดได้ 2 ถ้าปัดกลางทาง); * 7/8 = 21/16 = 1.3125 -> 1
        self.assertEqual(refund(5, 70, True), 1)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 10, True), 0)

    # ชนิดข้อมูลผิด -> ValueError
    def test_paid_rejects_float(self):
        with self.assertRaises(ValueError):
            refund(4500.0, 10, False)

    def test_paid_rejects_bool(self):
        with self.assertRaises(ValueError):
            refund(True, 10, False)

    def test_paid_rejects_none(self):
        with self.assertRaises(ValueError):
            refund(None, 10, False)

    def test_paid_rejects_str(self):
        with self.assertRaises(ValueError):
            refund("4500", 10, False)

    def test_paid_rejects_negative(self):
        with self.assertRaises(ValueError):
            refund(-1, 10, False)

    def test_used_percent_rejects_float(self):
        with self.assertRaises(ValueError):
            refund(4500, 10.0, False)

    def test_used_percent_rejects_bool(self):
        with self.assertRaises(ValueError):
            refund(4500, False, False)

    def test_used_percent_rejects_none(self):
        with self.assertRaises(ValueError):
            refund(4500, None, False)

    def test_used_percent_rejects_str(self):
        with self.assertRaises(ValueError):
            refund(4500, "10", False)

    def test_used_percent_rejects_below_range(self):
        with self.assertRaises(ValueError):
            refund(4500, -1, False)

    def test_used_percent_rejects_above_range(self):
        with self.assertRaises(ValueError):
            refund(4500, 101, False)

    def test_restock_rejects_int(self):
        with self.assertRaises(ValueError):
            refund(4500, 10, 1)

    def test_restock_rejects_none(self):
        with self.assertRaises(ValueError):
            refund(4500, 10, None)

    def test_restock_rejects_str(self):
        with self.assertRaises(ValueError):
            refund(4500, 10, "true")


class TestCli(unittest.TestCase):
    def test_cli_ok(self):
        proc = run_cli(json.dumps({"paid": 10000, "used_percent": 20, "restock": True}))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 7000})

    def test_cli_error(self):
        proc = run_cli(json.dumps({"paid": 10000.0, "used_percent": 20, "restock": True}))
        self.assertEqual(proc.returncode, 2)
        data = json.loads(proc.stdout)
        self.assertFalse(data["ok"])
        self.assertNotIn("Traceback", proc.stderr)

    def test_cli_bad_json(self):
        proc = run_cli("{not json")
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])

    def test_cli_missing_key(self):
        proc = run_cli(json.dumps({"paid": 10000, "used_percent": 20}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
