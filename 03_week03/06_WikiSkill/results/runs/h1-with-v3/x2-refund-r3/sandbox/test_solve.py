import json
import os
import subprocess
import sys
import unittest

from solve import refund

HERE = os.path.dirname(os.path.abspath(__file__))
SOLVE_PATH = os.path.join(HERE, "solve.py")


class RefundTests(unittest.TestCase):
    def test_no_usage_full_refund_without_restock(self):
        self.assertEqual(refund(1000, 0, False), 1000)

    def test_partial_usage_is_prorated(self):
        self.assertEqual(refund(1000, 30, False), 700)

    def test_restock_deducts_12_5_percent_of_refund(self):
        # 1000 * 80% = 800 คืน หักค่าดำเนินการ 100 เหลือ 700
        self.assertEqual(refund(1000, 20, True), 700)

    def test_over_80_percent_no_refund(self):
        self.assertEqual(refund(1000, 81, False), 0)
        self.assertEqual(refund(1000, 100, True), 0)

    def test_exactly_80_percent_still_refunds(self):
        self.assertEqual(refund(1000, 80, False), 200)

    def test_half_up_on_final_step_without_restock(self):
        # 5 * 50 หารด้วย 100 = 2 และครึ่ง ปัดขึ้นเป็น 3
        self.assertEqual(refund(5, 50, False), 3)

    def test_half_up_only_once_with_restock(self):
        # ยอดก่อนปัด 3 และครึ่งสตางค์ ปัดขึ้นเป็น 4 ครั้งเดียวตอนท้าย
        self.assertEqual(refund(4, 0, True), 4)

    def test_zero_paid_returns_zero(self):
        self.assertEqual(refund(0, 50, True), 0)

    def test_rejects_bad_inputs(self):
        bad_cases = [
            (True, 0, False),
            (1000, True, False),
            (1000, 0, 0),
            (None, 0, False),
            ("1000", 0, False),
            (10 * 2 ** -1, 0, False),  # ค่าทศนิยม 5.0 ต้องถูกปฏิเสธ
            (-1, 0, False),
            (1000, -1, False),
            (1000, 101, False),
        ]
        for paid, used, restock in bad_cases:
            with self.subTest(paid=paid, used=used, restock=restock):
                with self.assertRaises(ValueError):
                    refund(paid, used, restock)

    def _run_cli(self, stdin_text):
        proc = subprocess.run(
            [sys.executable, SOLVE_PATH],
            input=stdin_text,
            capture_output=True,
            text=True,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr

    def test_cli_success(self):
        code, out, _ = self._run_cli(
            json.dumps({"paid": 1000, "used_percent": 30, "restock": False})
        )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": 700})

    def test_cli_invalid_json_exit_2_without_traceback(self):
        code, out, err = self._run_cli("{bad json")
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(out)["ok"])
        self.assertNotIn("Traceback", err)

    def test_cli_missing_key_exit_2(self):
        code, out, _ = self._run_cli(json.dumps({"paid": 1000, "used_percent": 0}))
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(out)["ok"])


if __name__ == "__main__":
    unittest.main()
