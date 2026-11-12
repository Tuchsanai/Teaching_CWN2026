import json
import os
import subprocess
import sys
import unittest

from solve import late_fee

HERE = os.path.dirname(os.path.abspath(__file__))


class TestLateFee(unittest.TestCase):
    # ค่าที่คาดคำนวณด้วยมือ (ไม่ได้คัดลอกจากฟังก์ชัน)

    def test_normal_case(self):
        # 10000 * 0.75% * 4 = 300
        self.assertEqual(late_fee(10000, 4), 300)

    def test_boundary_free_days(self):
        # 3 วันยังไม่คิด, วันที่ 4 เริ่มคิด (นับทุกวันรวม 3 วันแรก)
        self.assertEqual(late_fee(10000, 0), 0)
        self.assertEqual(late_fee(10000, 3), 0)
        self.assertEqual(late_fee(10000, 4), 300)

    def test_half_up_exact_half(self):
        # 50 * 0.75% * 4 = 1.5 -> ปัดขึ้นเป็น 2 (floor จะได้ 1)
        self.assertEqual(late_fee(50, 4), 2)

    def test_single_rounding_multi_step(self):
        # 1 * 0.75% * 4 = 0.03 -> 0 ; ไม่ปัดระหว่างทาง
        self.assertEqual(late_fee(1, 4), 0)
        # 3 * 0.75% * 4 = 0.09 -> 0 ; 67 * 0.75% * 4 = 2.01 -> 2
        self.assertEqual(late_fee(67, 4), 2)

    def test_cap_boundary(self):
        # ยอด 100: เพดาน 15 สตางค์ ถึงที่วันที่ 20 (100 * 0.75% * 20 = 15)
        self.assertEqual(late_fee(100, 19), 14)   # 14.25 -> 14
        self.assertEqual(late_fee(100, 20), 15)   # 15 เท่าเพดานพอดี
        self.assertEqual(late_fee(100, 21), 15)   # 15.75 ถูกจำกัดที่ 15

    def test_cap_max_days(self):
        # 100 * 0.75% * 365 = 273.75 -> ถูกจำกัดที่ 15% = 15
        self.assertEqual(late_fee(100, 365), 15)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 365), 0)

    def test_rejects_float_amount(self):
        with self.assertRaises(ValueError):
            late_fee(4500.0, 4)

    def test_rejects_bool(self):
        with self.assertRaises(ValueError):
            late_fee(True, 4)
        with self.assertRaises(ValueError):
            late_fee(10000, False)

    def test_rejects_str_and_none(self):
        with self.assertRaises(ValueError):
            late_fee("10000", 4)
        with self.assertRaises(ValueError):
            late_fee(None, 4)
        with self.assertRaises(ValueError):
            late_fee(10000, "4")
        with self.assertRaises(ValueError):
            late_fee(10000, None)

    def test_rejects_negative_amount(self):
        with self.assertRaises(ValueError):
            late_fee(-1, 4)

    def test_rejects_days_out_of_range(self):
        with self.assertRaises(ValueError):
            late_fee(10000, -1)
        with self.assertRaises(ValueError):
            late_fee(10000, 366)

    def test_rejects_float_days(self):
        with self.assertRaises(ValueError):
            late_fee(10000, 4.0)


class TestCli(unittest.TestCase):
    def _run(self, payload):
        return subprocess.run(
            [sys.executable, "solve.py"],
            input=payload,
            capture_output=True,
            text=True,
            cwd=HERE,
        )

    def test_cli_ok(self):
        proc = self._run(json.dumps({"amount": 10000, "days_late": 4}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 300})

    def test_cli_error(self):
        proc = self._run(json.dumps({"amount": 4500.0, "days_late": 4}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
