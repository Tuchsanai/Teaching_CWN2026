import json
import subprocess
import sys
import unittest

from solve import cashback


class CashbackTests(unittest.TestCase):
    # ค่าคาดคำนวณด้วยมือ (ดูหมายเหตุในคอมเมนต์)

    def test_silver_normal(self):
        # 10000 * 1.5% = 150
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_gold_normal(self):
        # 10000 * 2.5% = 250
        self.assertEqual(cashback(10000, "gold", False), 250)

    def test_platinum_normal(self):
        # 10000 * 4% = 400
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_threshold_just_below(self):
        # 9999 < 100 บาท -> 0
        self.assertEqual(cashback(9999, "platinum", False), 0)

    def test_threshold_exact(self):
        # 10000 พอดี ได้เงินคืน: 10000 * 1.5% = 150
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_zero_amount(self):
        self.assertEqual(cashback(0, "gold", True), 0)

    def test_birthday_doubles(self):
        # 10000 * 2.5% * 2 = 500
        self.assertEqual(cashback(10000, "gold", True), 500)

    def test_half_up_rounding(self):
        # 10020 * 2.5% = 250.5 -> 251 (half up)
        self.assertEqual(cashback(10020, "gold", False), 251)

    def test_single_rounding_with_birthday(self):
        # 10017 * 1.5% * 2 = 300.51 -> 301
        # (ถ้าปัดกลางทางเป็น 150 ก่อนคูณ 2 จะได้ 300 ผิด)
        self.assertEqual(cashback(10017, "silver", True), 301)

    def test_cap_applied(self):
        # 500000 * 4% = 20000 พอดีเพดาน
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_cap_after_birthday(self):
        # 250000 * 4% * 2 = 20000 -> เพดาน 20000
        self.assertEqual(cashback(250000, "platinum", True), 20000)
        # 1,000,000 * 1.5% * 2 = 30000 -> ถูกตัดเหลือ 20000
        self.assertEqual(cashback(1000000, "silver", True), 20000)

    def test_just_below_cap(self):
        # 499999 * 4% = 19999.96 -> 20000 (half up) -> เพดาน 20000
        self.assertEqual(cashback(499999, "platinum", False), 20000)
        # 100000 * 1.5% = 1500 (ไม่ถึงเพดาน)
        self.assertEqual(cashback(100000, "silver", False), 1500)

    def test_invalid_amount(self):
        for bad in [-1, 10000.0, "10000", None, True]:
            with self.subTest(amount=bad):
                with self.assertRaises(ValueError):
                    cashback(bad, "silver", False)

    def test_invalid_tier(self):
        for bad in ["Silver", "bronze", "", None, 1]:
            with self.subTest(tier=bad):
                with self.assertRaises(ValueError):
                    cashback(10000, bad, False)

    def test_invalid_birthday(self):
        for bad in [1, 0, "true", None]:
            with self.subTest(birthday=bad):
                with self.assertRaises(ValueError):
                    cashback(10000, "silver", bad)


class CliTests(unittest.TestCase):
    def _run(self, payload):
        return subprocess.run(
            [sys.executable, "solve.py"],
            input=payload,
            capture_output=True,
            text=True,
        )

    def test_cli_ok(self):
        p = self._run(json.dumps({"amount": 10000, "tier": "gold", "birthday": True}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 500})

    def test_cli_error(self):
        p = self._run(json.dumps({"amount": 10000.0, "tier": "gold", "birthday": True}))
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])
        self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
