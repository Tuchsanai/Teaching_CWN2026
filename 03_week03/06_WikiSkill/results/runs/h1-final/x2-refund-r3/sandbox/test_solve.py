import json
import subprocess
import sys
import unittest

from solve import refund


class TestRefund(unittest.TestCase):
    # ค่าที่คาดคำนวณด้วยมือ (เศษส่วน) แยกจากโค้ด

    def test_normal_no_restock(self):
        # 10000 * 75/100 = 7500
        self.assertEqual(refund(10000, 25, False), 7500)

    def test_normal_with_restock(self):
        # 10000 * 75/100 * 7/8 = 6562.5 -> 6563 (half up)
        self.assertEqual(refund(10000, 25, True), 6563)

    def test_no_used_full_refund(self):
        self.assertEqual(refund(1000, 0, False), 1000)

    def test_zero_paid(self):
        self.assertEqual(refund(0, 0, True), 0)

    def test_half_up_exact_point_five_rounds_up(self):
        # 3 * 50/100 = 1.5 -> 2
        self.assertEqual(refund(3, 50, False), 2)
        # 4 * 7/8 = 3.5 -> 4
        self.assertEqual(refund(4, 0, True), 4)

    def test_single_rounding_at_end(self):
        # 1 * 50/100 * 7/8 = 0.4375 -> 0
        # ถ้าปัดกลางทางเป็น 1 แล้วค่อยหัก 12.5% จะได้ 1 (ผิด)
        self.assertEqual(refund(1, 50, True), 0)

    def test_restock_rounding_1001(self):
        # 1001 * 7/8 = 875.875 -> 876
        self.assertEqual(refund(1001, 0, True), 876)

    def test_threshold_80_is_refundable(self):
        # ที่ 80% ยังคืน: 1000 * 20/100 = 200
        self.assertEqual(refund(1000, 80, False), 200)
        # 200 * 7/8 = 175
        self.assertEqual(refund(1000, 80, True), 175)

    def test_threshold_above_80_no_refund(self):
        self.assertEqual(refund(1000, 81, False), 0)
        self.assertEqual(refund(1000, 81, True), 0)
        self.assertEqual(refund(1000, 100, False), 0)

    def test_invalid_paid(self):
        for bad in (4500.0, True, -1, "100", None):
            with self.subTest(paid=bad):
                with self.assertRaises(ValueError):
                    refund(bad, 0, False)

    def test_invalid_used_percent(self):
        for bad in (-1, 101, 50.0, True, "10", None):
            with self.subTest(used_percent=bad):
                with self.assertRaises(ValueError):
                    refund(1000, bad, False)

    def test_invalid_restock(self):
        for bad in (1, 0, "yes", None):
            with self.subTest(restock=bad):
                with self.assertRaises(ValueError):
                    refund(1000, 0, bad)


class TestCLI(unittest.TestCase):
    def _run(self, payload):
        return subprocess.run(
            [sys.executable, "solve.py"],
            input=payload,
            capture_output=True,
            text=True,
        )

    def test_cli_ok(self):
        p = self._run(json.dumps({"paid": 10000, "used_percent": 25, "restock": False}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 7500})

    def test_cli_invalid_value(self):
        p = self._run(json.dumps({"paid": 1.5, "used_percent": 25, "restock": False}))
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])

    def test_cli_missing_key(self):
        p = self._run(json.dumps({"paid": 1000, "used_percent": 25}))
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])

    def test_cli_bad_json(self):
        p = self._run("{not json")
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
