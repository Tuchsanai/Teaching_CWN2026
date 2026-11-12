import json
import subprocess
import sys
import unittest

from solve import late_fee


class TestLateFee(unittest.TestCase):
    def test_no_fee_within_grace(self):
        # ช้า 0-3 วัน ไม่คิดค่าปรับ
        self.assertEqual(late_fee(10000, 0), 0)
        self.assertEqual(late_fee(10000, 3), 0)

    def test_fee_starts_after_three_days(self):
        # 4 วัน: 10000 * 0.75% * 4 = 300 (นับรวม 3 วันแรกเมื่อเกินเกณฑ์)
        self.assertEqual(late_fee(10000, 4), 300)
        # 5 วัน: 10000 * 0.75% * 5 = 375
        self.assertEqual(late_fee(10000, 5), 375)

    def test_cap_boundary(self):
        # 20 วัน: 0.75% * 20 = 15% พอดี -> 1500 (ยังไม่ถึงเพดานเกิน)
        self.assertEqual(late_fee(10000, 20), 1500)
        # 21 วัน: raw 1575 เกินเพดาน 1500 -> 1500
        self.assertEqual(late_fee(10000, 21), 1500)
        # 365 วัน ยังถูกจำกัดที่ 15%
        self.assertEqual(late_fee(10000, 365), 1500)

    def test_half_up_rounding(self):
        # 50 * 0.75% * 4 = 1.5 -> ปัดขึ้นเป็น 2 (floor จะได้ 1)
        self.assertEqual(late_fee(50, 4), 2)

    def test_single_rounding_at_end(self):
        # 333 * 75 * 7 / 10000 = 17.4825 -> 17
        self.assertEqual(late_fee(333, 7), 17)
        # cap = 15% ของ 10 = 1.5 -> ปัดครั้งเดียวเป็น 2
        self.assertEqual(late_fee(10, 365), 2)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 30), 0)

    def test_reject_invalid_amount(self):
        for bad in (4500.0, True, None, "4500", -1):
            with self.subTest(amount=bad):
                with self.assertRaises(ValueError):
                    late_fee(bad, 5)

    def test_reject_invalid_days(self):
        for bad in (4.0, True, None, "5", -1, 366):
            with self.subTest(days_late=bad):
                with self.assertRaises(ValueError):
                    late_fee(10000, bad)

    def test_cli_ok(self):
        r = subprocess.run(
            [sys.executable, "solve.py"],
            input=json.dumps({"amount": 10000, "days_late": 4}),
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 300})

    def test_cli_error(self):
        r = subprocess.run(
            [sys.executable, "solve.py"],
            input=json.dumps({"amount": 10000.0, "days_late": 4}),
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 2)
        out = json.loads(r.stdout)
        self.assertFalse(out["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
